"""Generate all documentation types from repo analysis."""
from app.services.llm_client import chat


def _repo_ctx(analysis: dict, files: list[dict]) -> str:
    sample = "\n\n".join(
        f"### {f['path']}\n```\n{f['content'][:1500]}\n```"
        for f in files[:25]
    )
    return f"""Repository: {analysis.get('name','unknown')}
Architecture: {analysis.get('arch_type')}
Languages: {', '.join(analysis.get('languages', []))}
Frameworks: {', '.join(analysis.get('frameworks', []))}
Databases: {', '.join(analysis.get('databases', []))}
Auth: {', '.join(analysis.get('auth_methods', []))}
Files ({analysis.get('file_count',0)} total, {analysis.get('loc_total',0)} LOC):

{sample}"""


SYS = "You are a senior software engineer creating production-quality technical documentation. Be precise, thorough, and well-structured."


async def generate_summary(analysis: dict, files: list[dict]) -> str:
    ctx = _repo_ctx(analysis, files)
    return await chat(SYS, f"""Write an executive summary for this repository.

{ctx}

Include:
1. What the project does (2-3 sentences)
2. Who it's for
3. Key technical highlights
4. Current maturity / production-readiness

Format: Markdown. Be concise but complete.""")


async def generate_architecture(analysis: dict, files: list[dict]) -> str:
    ctx = _repo_ctx(analysis, files)
    return await chat(SYS, f"""Write a detailed architecture overview for this repository.

{ctx}

Include:
1. System architecture style ({analysis.get('arch_type')})
2. Component breakdown
3. Data flow description
4. Key design decisions
5. External dependencies and integrations
6. Folder structure map with purpose of each major directory

Format: Markdown with clear sections.""")


async def generate_folder_explainer(files: list[dict], name: str) -> str:
    tree = "\n".join(f["path"] for f in files[:200])
    sample = "\n\n".join(
        f"**{f['path']}** ({f['language']})\n```\n{f['content'][:800]}\n```"
        for f in files[:20]
    )
    return await chat(SYS, f"""Explain every major folder and file in the repository "{name}".

File tree:
{tree}

Sample files:
{sample}

For each top-level directory and important file:
- What is its purpose?
- What does it contain?
- How does it relate to the rest of the system?

Format: Markdown. Group by directory.""")


async def generate_setup_guide(analysis: dict, files: list[dict]) -> str:
    env_sample = next((f["content"][:2000] for f in files if ".env" in f["path"] or "env.example" in f["path"]), "")
    docker_sample = next((f["content"][:2000] for f in files if "docker" in f["path"].lower()), "")
    pkg = next((f["content"][:3000] for f in files if f["path"] == "package.json"), "")
    req = next((f["content"][:2000] for f in files if "requirements" in f["path"]), "")

    return await chat(SYS, f"""Write a complete setup guide for this repository.

Stack: {', '.join(analysis.get('frameworks',[]))}
Package managers: {', '.join(analysis.get('package_managers',[]))}
Databases: {', '.join(analysis.get('databases',[]))}

.env sample:
{env_sample}

Docker config:
{docker_sample}

Package.json:
{pkg}

Requirements.txt:
{req}

Include:
1. Prerequisites
2. Installation steps (numbered, copy-paste ready)
3. Environment variable configuration
4. Database setup
5. Running locally
6. Running with Docker (if applicable)
7. Running tests
8. Common troubleshooting

Format: Markdown with code blocks.""")


async def generate_api_docs(files: list[dict], name: str) -> str:
    api_files = [f for f in files if any(x in f["path"].lower() for x in ["route","api","endpoint","controller","handler","view"])]
    sample = "\n\n".join(
        f"### {f['path']}\n```\n{f['content'][:2000]}\n```"
        for f in api_files[:15]
    )
    return await chat(SYS, f"""Generate complete API documentation for "{name}".

API/Route files:
{sample}

For each endpoint found:
- Method + path
- Description
- Request body / query params
- Response schema
- Auth requirement
- Example request/response

Format: Markdown. Group by resource/module.""")


async def generate_readme(analysis: dict, files: list[dict]) -> str:
    ctx = _repo_ctx(analysis, files)
    return await chat(SYS, f"""Generate a production-quality README.md for this repository.

{ctx}

Include:
# Project Name
Badges (build, license, version)

## Overview
## Features
## Tech Stack
## Prerequisites
## Installation
## Usage
## API Reference (brief)
## Architecture
## Contributing
## License

Make it look professional, like a top open-source project.""")


async def generate_recruiter(analysis: dict, files: list[dict]) -> str:
    ctx = _repo_ctx(analysis, files)
    return await chat(SYS, f"""Generate recruiter-friendly content for this project.

{ctx}

Generate:

## Resume Bullet Points (5 strong bullets, quantify impact)

## ATS-Friendly Project Description (150 words, keyword-rich)

## STAR Interview Explanation
- Situation
- Task
- Action
- Result

## Technical Summary (for technical recruiters)

## Elevator Pitch (30 seconds, plain English)

Use strong action verbs. Highlight scale, impact, and technical sophistication.""")


async def generate_interview_questions(analysis: dict, files: list[dict]) -> str:
    ctx = _repo_ctx(analysis, files)
    return await chat(SYS, f"""Generate interview questions about this codebase.

{ctx}

Generate:

## Beginner Questions (5 questions + answers)
Focus on: what the project does, basic architecture, how to run it.

## Intermediate Questions (5 questions + answers)
Focus on: design decisions, database schema, API design, authentication.

## Advanced Questions (5 questions + answers)
Focus on: scaling, performance, security, trade-offs, improvements.

Each answer should reference specific files or patterns from the actual codebase.""")


async def generate_onboarding(analysis: dict, files: list[dict]) -> dict:
    ctx = _repo_ctx(analysis, files)
    tree = "\n".join(f["path"] for f in files[:100])

    content = await chat(SYS, f"""Create a 3-day developer onboarding guide for a new engineer joining this project.

{ctx}

File tree:
{tree}

## Day 1: Orientation
- Overview of the project
- Files to read first (list with reasons)
- How to set up the development environment
- Key concepts to understand

## Day 2: Deep Dive
- Core business logic files to study
- Database schema walkthrough
- API structure walkthrough
- Running and debugging

## Day 3: Contributing
- Writing your first feature
- Testing approach
- Code style and conventions
- Deployment workflow

Also list: Top 10 most important files to understand the codebase.""")

    lines = content.split("\n")
    day1_lines, day2_lines, day3_lines, key_files = [], [], [], []
    current = None
    for line in lines:
        if "## Day 1" in line: current = "d1"
        elif "## Day 2" in line: current = "d2"
        elif "## Day 3" in line: current = "d3"
        elif "most important" in line.lower(): current = "kf"
        elif current == "d1": day1_lines.append(line)
        elif current == "d2": day2_lines.append(line)
        elif current == "d3": day3_lines.append(line)
        elif current == "kf" and line.strip().startswith("-"):
            key_files.append(line.strip().lstrip("- "))

    return {
        "day1": "\n".join(day1_lines).strip() or content[:1000],
        "day2": "\n".join(day2_lines).strip() or content[1000:2000],
        "day3": "\n".join(day3_lines).strip() or content[2000:3000],
        "key_files": key_files[:10],
        "checklist": ["Set up dev environment", "Read the README", "Run the project locally", "Read the API docs", "Make a small change"],
    }
