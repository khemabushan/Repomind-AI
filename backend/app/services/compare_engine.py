"""Compare two repositories across multiple dimensions."""
from app.services.llm_client import chat


async def compare_repos(analysis_a: dict, analysis_b: dict, files_a: list[dict], files_b: list[dict], complexity_a: dict, complexity_b: dict) -> dict:
    score_matrix = {
        "tech_stack": _compare_tech(analysis_a, analysis_b),
        "architecture": _compare_arch(analysis_a, analysis_b),
        "complexity": _compare_complexity(complexity_a, complexity_b),
        "documentation": {"a": complexity_a.get("documentation",0), "b": complexity_b.get("documentation",0)},
        "maintainability": {"a": complexity_a.get("maintainability",0), "b": complexity_b.get("maintainability",0)},
        "test_coverage": {"a": complexity_a.get("test_coverage",0), "b": complexity_b.get("test_coverage",0)},
        "overall": {"a": complexity_a.get("overall",0), "b": complexity_b.get("overall",0)},
        "loc": {"a": analysis_a.get("loc_total",0), "b": analysis_b.get("loc_total",0)},
        "file_count": {"a": analysis_a.get("file_count",0), "b": analysis_b.get("file_count",0)},
    }

    summary = await _generate_summary(analysis_a, analysis_b, score_matrix)
    return {"score_matrix": score_matrix, "summary": summary, "tech_stack_diff": _tech_diff(analysis_a, analysis_b)}


def _compare_tech(a: dict, b: dict) -> dict:
    return {
        "a": {"languages": a.get("languages",[]), "frameworks": a.get("frameworks",[]), "databases": a.get("databases",[])},
        "b": {"languages": b.get("languages",[]), "frameworks": b.get("frameworks",[]), "databases": b.get("databases",[])},
        "shared_frameworks": list(set(a.get("frameworks",[])) & set(b.get("frameworks",[]))),
        "shared_languages":  list(set(a.get("languages",[])) & set(b.get("languages",[]))),
    }


def _compare_arch(a: dict, b: dict) -> dict:
    return {
        "a": {"type": a.get("arch_type"), "patterns": a.get("design_patterns",[]), "auth": a.get("auth_methods",[])},
        "b": {"type": b.get("arch_type"), "patterns": b.get("design_patterns",[]), "auth": b.get("auth_methods",[])},
    }


def _compare_complexity(c_a: dict, c_b: dict) -> dict:
    return {
        "a": c_a.get("overall", 0),
        "b": c_b.get("overall", 0),
        "winner": "a" if c_a.get("overall", 0) >= c_b.get("overall", 0) else "b",
    }


def _tech_diff(a: dict, b: dict) -> dict:
    return {
        "only_in_a": {
            "frameworks": list(set(a.get("frameworks",[])) - set(b.get("frameworks",[]))),
            "languages":  list(set(a.get("languages",[])) - set(b.get("languages",[]))),
            "databases":  list(set(a.get("databases",[])) - set(b.get("databases",[]))),
        },
        "only_in_b": {
            "frameworks": list(set(b.get("frameworks",[])) - set(a.get("frameworks",[]))),
            "languages":  list(set(b.get("languages",[])) - set(a.get("languages",[]))),
            "databases":  list(set(b.get("databases",[])) - set(a.get("databases",[]))),
        },
    }


async def _generate_summary(a: dict, b: dict, matrix: dict) -> str:
    return await chat(
        "You are a senior software architect. Compare these two repositories objectively.",
        f"""Compare Repository A ({a.get('name','A')}) vs Repository B ({b.get('name','B')}).

Scores (0-100):
- Overall Quality: A={matrix['overall']['a']} vs B={matrix['overall']['b']}
- Maintainability: A={matrix['maintainability']['a']} vs B={matrix['maintainability']['b']}
- Documentation:   A={matrix['documentation']['a']} vs B={matrix['documentation']['b']}
- Test Coverage:   A={matrix['test_coverage']['a']}% vs B={matrix['test_coverage']['b']}%

Tech Stack A: {a.get('frameworks',[])} + {a.get('databases',[])}
Tech Stack B: {b.get('frameworks',[])} + {b.get('databases',[])}

Architecture A: {a.get('arch_type')} | Auth: {a.get('auth_methods',[])}
Architecture B: {b.get('arch_type')} | Auth: {b.get('auth_methods',[])}

Write a 4-paragraph comparison:
1. Overall assessment — which is better quality overall and why
2. Tech stack comparison — trade-offs and use cases
3. Architecture comparison — strengths and weaknesses
4. Recommendation — when to use each one

Be specific and objective."""
    )
