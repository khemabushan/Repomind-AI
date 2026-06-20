"""Generate Mermaid diagram source for different diagram types."""
from app.services.llm_client import chat

SYS = "You are a software architect. Output ONLY valid Mermaid diagram syntax. No markdown fences, no explanation."


async def generate_component_diagram(analysis: dict, files: list[dict]) -> str:
    ctx = _ctx(analysis, files)
    raw = await chat(SYS, f"""Generate a Mermaid component/architecture diagram for this system.

{ctx}

Use 'graph TD' syntax. Show:
- Main components/services
- How they connect
- External dependencies (DB, APIs, auth)
- Direction of data flow

Example style:
graph TD
    A[Frontend React] --> B[API Gateway]
    B --> C[Auth Service]
    B --> D[Database]

Output ONLY the Mermaid syntax.""")
    return _clean(raw)


async def generate_dataflow_diagram(analysis: dict, files: list[dict]) -> str:
    ctx = _ctx(analysis, files)
    raw = await chat(SYS, f"""Generate a Mermaid data flow diagram for this system.

{ctx}

Use 'flowchart LR' syntax. Show:
- How data enters the system
- Processing steps
- Storage
- Output/responses

Output ONLY the Mermaid syntax.""")
    return _clean(raw)


async def generate_api_flow_diagram(files: list[dict], name: str) -> str:
    api_files = [f for f in files if any(x in f["path"].lower() for x in ["route","api","endpoint","controller","handler"])]
    sample = "\n\n".join(f"### {f['path']}\n{f['content'][:1000]}" for f in api_files[:8])
    raw = await chat(SYS, f"""Generate a Mermaid sequence diagram showing API request flows for "{name}".

API files:
{sample}

Use 'sequenceDiagram' syntax. Show:
- Client → Server requests
- Server → Database queries
- Authentication flow
- Response flow

Output ONLY the Mermaid syntax.""")
    return _clean(raw)


async def generate_db_diagram(files: list[dict], name: str) -> str:
    db_files = [f for f in files if any(x in f["path"].lower() for x in ["model","schema","migration","entity","prisma","sequelize"])]
    sample = "\n\n".join(f"### {f['path']}\n{f['content'][:1500]}" for f in db_files[:10])
    raw = await chat(SYS, f"""Generate a Mermaid entity-relationship diagram for "{name}".

Schema/model files:
{sample}

Use 'erDiagram' syntax with:
- Entities (tables/models)
- Relationships (||--o{{, etc.)
- Key attributes per entity

Output ONLY the Mermaid syntax.""")
    return _clean(raw)


def _ctx(analysis: dict, files: list[dict]) -> str:
    return f"""Architecture: {analysis.get('arch_type')}
Frameworks: {', '.join(analysis.get('frameworks', []))}
Databases: {', '.join(analysis.get('databases', []))}
Auth: {', '.join(analysis.get('auth_methods', []))}
Key files: {', '.join(f['path'] for f in files[:30])}"""


def _clean(raw: str) -> str:
    raw = raw.strip()
    for fence in ["```mermaid", "```"]:
        raw = raw.replace(fence, "")
    return raw.strip()
