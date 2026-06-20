"""Analyze code complexity metrics and generate scores."""
import re
from app.services.llm_client import chat


def compute_complexity(files: list[dict], analysis: dict) -> dict:
    py_files = [f for f in files if f["language"] == "Python"]
    js_files = [f for f in files if f["language"] in ("JavaScript","TypeScript")]
    test_files = [f for f in files if any(x in f["path"].lower() for x in ["test","spec","__tests__"])]
    doc_files  = [f for f in files if f["path"].endswith(".md")]

    file_count = max(len(files), 1)
    loc = sum(f["content"].count("\n") for f in files)
    test_pct = round(len(test_files) / file_count * 100, 1)
    doc_score = min(100, len(doc_files) * 20 + (50 if any("README" in f["path"] for f in files) else 0))

    # Cyclomatic complexity heuristic (count control flow keywords)
    cc_scores = []
    for f in files:
        t = f["content"]
        cc = t.count(" if ") + t.count(" for ") + t.count(" while ") + t.count(" case ") + t.count(" catch ") + t.count(" elif ") + t.count(" else:") + t.count(" else {")
        lines = max(t.count("\n"), 1)
        cc_scores.append(min(100, max(0, 100 - int(cc / lines * 500))))

    maintainability = int(sum(cc_scores) / max(len(cc_scores), 1))
    architecture_score = _arch_score(analysis)

    # hotspot files: high cc
    hotspots = []
    for i, f in enumerate(files):
        if i < len(cc_scores) and cc_scores[i] < 50:
            hotspots.append(f["path"])

    overall = int((maintainability + doc_score + architecture_score + min(100, test_pct * 2)) / 4)
    tech_debt = max(0, 100 - overall)

    return {
        "overall": overall,
        "maintainability": maintainability,
        "documentation": doc_score,
        "architecture": architecture_score,
        "test_coverage": test_pct,
        "tech_debt": tech_debt,
        "hotspots": hotspots[:10],
        "file_scores": {f["path"]: cc_scores[i] for i, f in enumerate(files[:50])},
    }


def _arch_score(analysis: dict) -> int:
    score = 50
    if analysis.get("design_patterns"): score += min(30, len(analysis["design_patterns"]) * 5)
    if analysis.get("databases"): score += 10
    if analysis.get("deployment_configs"): score += 10
    return min(100, score)


async def generate_analysis_report(scores: dict, analysis: dict, files: list[dict]) -> dict:
    ctx = f"""Scores:
- Overall: {scores['overall']}/100
- Maintainability: {scores['maintainability']}/100
- Documentation: {scores['documentation']}/100
- Architecture: {scores['architecture']}/100
- Test Coverage: {scores['test_coverage']}%
- Tech Debt: {scores['tech_debt']}/100
- Hotspot files: {', '.join(scores['hotspots'][:5])}

Stack: {', '.join(analysis.get('frameworks',[]))}
Patterns: {', '.join(analysis.get('design_patterns',[]))}
File count: {len(files)}, LOC: {sum(f['content'].count(chr(10)) for f in files)}"""

    report = await chat(
        "You are a senior code reviewer. Be specific, actionable, and professional.",
        f"""Analyze this repository's code quality and generate a report.

{ctx}

Generate JSON with exactly these keys:
{{
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2", "weakness3"],
  "suggestions": ["suggestion1", "suggestion2", "suggestion3", "suggestion4", "suggestion5"]
}}

Be specific to the actual tech stack. Strengths/weaknesses should be 1-2 sentences each."""
    )

    import json, re
    try:
        m = re.search(r'\{.*\}', report, re.DOTALL)
        if m:
            data = json.loads(m.group())
            return data
    except Exception:
        pass
    return {
        "strengths": ["Clean code structure", "Modern framework usage", "Clear separation of concerns"],
        "weaknesses": ["Limited test coverage", "Sparse inline documentation"],
        "suggestions": ["Add unit tests", "Add API documentation", "Set up CI/CD", "Add error handling", "Add logging"],
    }
