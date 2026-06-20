"""Background worker: runs the full analysis pipeline for a repo."""
import logging
from datetime import datetime, timezone

from app.db.session import AsyncSessionLocal
from app.models import (
    Repo, Job, Analysis, Document, Chunk,
    ComplexityScore, MermaidDiagram, OnboardingGuide,
)
from app.services import (
    repo_cloner, arch_detector, doc_generator,
    complexity_analyzer, mermaid_generator, rag_engine,
)

log = logging.getLogger(__name__)


async def _set_job(job_id: str, step: str, progress: int, status: str = "running"):
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if job:
            job.step = step
            job.progress = progress
            job.status = status
            await db.commit()


async def run_analysis(repo_id: str, job_id: str):
    try:
        # ── 1. Clone ──────────────────────────────────────────────────────
        await _set_job(job_id, "cloning", 5)
        async with AsyncSessionLocal() as db:
            repo = await db.get(Repo, repo_id)
            url = repo.url
            name = repo.name

        cloned_path = repo_cloner.clone_repo(url, repo_id)

        async with AsyncSessionLocal() as db:
            repo = await db.get(Repo, repo_id)
            repo.cloned_path = cloned_path
            repo.status = "parsing"
            await db.commit()

        # ── 2. Parse files ────────────────────────────────────────────────
        await _set_job(job_id, "parsing", 15)
        files = repo_cloner.walk_repo(cloned_path)
        loc = repo_cloner.count_loc(files)

        # ── 3. Detect architecture ────────────────────────────────────────
        await _set_job(job_id, "detecting", 22)
        detected = arch_detector.detect_all(files)
        analysis_dict = {**detected, "name": name, "file_count": len(files), "loc_total": loc}

        async with AsyncSessionLocal() as db:
            db.add(Analysis(
                repo_id=repo_id,
                arch_type=detected["arch_type"],
                languages=detected["languages"],
                frameworks=detected["frameworks"],
                databases=detected["databases"],
                auth_methods=detected["auth_methods"],
                design_patterns=detected["design_patterns"],
                package_managers=detected["package_managers"],
                deployment_configs=detected["deployment_configs"],
                file_count=len(files),
                loc_total=loc,
            ))
            await db.commit()

        # ── 4. Generate documents ─────────────────────────────────────────
        doc_tasks = [
            ("summary",    doc_generator.generate_summary(analysis_dict, files)),
            ("architecture", doc_generator.generate_architecture(analysis_dict, files)),
            ("folder",     doc_generator.generate_folder_explainer(files, name)),
            ("setup_guide", doc_generator.generate_setup_guide(analysis_dict, files)),
            ("api_docs",   doc_generator.generate_api_docs(files, name)),
            ("readme",     doc_generator.generate_readme(analysis_dict, files)),
            ("recruiter",  doc_generator.generate_recruiter(analysis_dict, files)),
            ("interview",  doc_generator.generate_interview_questions(analysis_dict, files)),
        ]

        for idx, (doc_type, coro) in enumerate(doc_tasks):
            await _set_job(job_id, f"generating_{doc_type}", 25 + idx * 6)
            try:
                content = await coro
                async with AsyncSessionLocal() as db:
                    db.add(Document(repo_id=repo_id, doc_type=doc_type, content=content, tokens_used=len(content) // 4))
                    await db.commit()
            except Exception as e:
                log.warning(f"[{repo_id}] doc {doc_type} failed: {e}")

        # ── 5. Onboarding ─────────────────────────────────────────────────
        await _set_job(job_id, "onboarding", 74)
        try:
            onb = await doc_generator.generate_onboarding(analysis_dict, files)
            async with AsyncSessionLocal() as db:
                db.add(OnboardingGuide(
                    repo_id=repo_id,
                    day1=onb["day1"], day2=onb["day2"], day3=onb["day3"],
                    key_files=onb["key_files"], checklist=onb["checklist"],
                ))
                await db.commit()
        except Exception as e:
            log.warning(f"[{repo_id}] onboarding failed: {e}")

        # ── 6. Complexity ─────────────────────────────────────────────────
        await _set_job(job_id, "complexity", 78)
        try:
            scores = complexity_analyzer.compute_complexity(files, analysis_dict)
            report = await complexity_analyzer.generate_analysis_report(scores, analysis_dict, files)
            async with AsyncSessionLocal() as db:
                db.add(ComplexityScore(
                    repo_id=repo_id,
                    overall=scores["overall"],
                    maintainability=scores["maintainability"],
                    documentation=scores["documentation"],
                    architecture=scores["architecture"],
                    test_coverage=scores["test_coverage"],
                    tech_debt=scores["tech_debt"],
                    hotspots=scores["hotspots"],
                    file_scores=scores["file_scores"],
                    strengths=report.get("strengths", []),
                    weaknesses=report.get("weaknesses", []),
                    suggestions=report.get("suggestions", []),
                ))
                await db.commit()
        except Exception as e:
            log.warning(f"[{repo_id}] complexity failed: {e}")

        # ── 7. Mermaid diagrams ───────────────────────────────────────────
        await _set_job(job_id, "diagrams", 84)
        diag_tasks = [
            ("component", mermaid_generator.generate_component_diagram(analysis_dict, files)),
            ("dataflow",  mermaid_generator.generate_dataflow_diagram(analysis_dict, files)),
            ("api_flow",  mermaid_generator.generate_api_flow_diagram(files, name)),
            ("database",  mermaid_generator.generate_db_diagram(files, name)),
        ]
        for dtype, coro in diag_tasks:
            try:
                src = await coro
                async with AsyncSessionLocal() as db:
                    db.add(MermaidDiagram(repo_id=repo_id, diagram_type=dtype, source=src))
                    await db.commit()
            except Exception as e:
                log.warning(f"[{repo_id}] diagram {dtype} failed: {e}")

        # ── 8. RAG index ──────────────────────────────────────────────────
        await _set_job(job_id, "indexing", 93)
        try:
            rag_engine.build_index(repo_id, files)
            async with AsyncSessionLocal() as db:
                for f in files[:300]:
                    db.add(Chunk(
                        repo_id=repo_id,
                        file_path=f["path"],
                        content=f["content"][:2000],
                        language=f["language"],
                    ))
                await db.commit()
        except Exception as e:
            log.warning(f"[{repo_id}] RAG indexing failed: {e}")

        # ── Done ──────────────────────────────────────────────────────────
        async with AsyncSessionLocal() as db:
            repo = await db.get(Repo, repo_id)
            job  = await db.get(Job, job_id)
            if repo:
                repo.status = "complete"
            if job:
                job.status   = "complete"
                job.progress = 100
                job.step     = "done"
                job.finished_at = datetime.now(timezone.utc)
            await db.commit()
        log.info(f"[{repo_id}] analysis complete")

    except Exception as e:
        log.error(f"[{repo_id}] analysis FAILED: {e}", exc_info=True)
        async with AsyncSessionLocal() as db:
            repo = await db.get(Repo, repo_id)
            job  = await db.get(Job, job_id)
            if repo:
                repo.status = "failed"
            if job:
                job.status     = "failed"
                job.error      = str(e)
                job.finished_at = datetime.now(timezone.utc)
            await db.commit()
