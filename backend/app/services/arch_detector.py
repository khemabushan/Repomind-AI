"""Detect architecture, frameworks, databases, auth patterns from file list."""
import json, re
from pathlib import Path


def detect_all(files: list[dict]) -> dict:
    paths  = [f["path"] for f in files]
    all_text = "\n".join(f["content"][:3000] for f in files[:50])
    pkg_content = _read_file(files, ["package.json"])
    req_content = _read_file(files, ["requirements.txt","pyproject.toml"])
    go_mod      = _read_file(files, ["go.mod"])

    return {
        "arch_type":          _arch_type(paths),
        "languages":          _languages(files),
        "frameworks":         _frameworks(paths, pkg_content, req_content, go_mod),
        "databases":          _databases(paths, all_text),
        "auth_methods":       _auth(all_text),
        "design_patterns":    _patterns(paths, all_text),
        "package_managers":   _pkg_managers(paths),
        "deployment_configs": _deployment(paths),
    }


def _read_file(files: list[dict], names: list[str]) -> str:
    for f in files:
        if any(f["path"].endswith(n) for n in names):
            return f["content"]
    return ""


def _arch_type(paths: list[str]) -> str:
    p = " ".join(paths).lower()
    if any(x in p for x in ["microservice","services/","apps/"]): return "Microservices"
    if any(x in p for x in ["frontend","backend","api"]): return "Full-Stack"
    if "lambda" in p or "functions" in p: return "Serverless"
    if any(x in p for x in ["lib/","src/lib","packages/"]): return "Library / SDK"
    return "Monolith"


def _languages(files: list[dict]) -> list[str]:
    counts: dict[str,int] = {}
    for f in files:
        counts[f["language"]] = counts.get(f["language"], 0) + 1
    return sorted({l for l,c in counts.items() if c > 0 and l != "Text"}, key=lambda l: -counts[l])


def _frameworks(paths, pkg, req, go) -> list[str]:
    found = []
    p = " ".join(paths).lower()
    # JS/TS
    if pkg:
        try:
            data = json.loads(pkg)
            deps = {**data.get("dependencies",{}), **data.get("devDependencies",{})}
            MAP = {"react":"React","next":"Next.js","vue":"Vue.js","nuxt":"Nuxt.js","angular":"Angular","svelte":"Svelte","express":"Express","fastify":"Fastify","nestjs":"NestJS","hapi":"Hapi.js","koa":"Koa","vite":"Vite","webpack":"Webpack"}
            for k,v in MAP.items():
                if any(k in d.lower() for d in deps): found.append(v)
        except Exception: pass
    # Python
    if req:
        MAP2 = {"fastapi":"FastAPI","django":"Django","flask":"Flask","starlette":"Starlette","tornado":"Tornado","sqlalchemy":"SQLAlchemy","langchain":"LangChain","celery":"Celery"}
        for k,v in MAP2.items():
            if k in req.lower(): found.append(v)
    # Go
    if go:
        if "gin-gonic" in go: found.append("Gin")
        if "echo" in go: found.append("Echo")
        if "fiber" in go: found.append("Fiber")
    return list(dict.fromkeys(found))


def _databases(paths, text) -> list[str]:
    found = []
    checks = [("postgres","PostgreSQL"),("mysql","MySQL"),("sqlite","SQLite"),("mongodb","MongoDB"),("redis","Redis"),("elasticsearch","Elasticsearch"),("cassandra","Cassandra"),("dynamodb","DynamoDB"),("supabase","Supabase"),("prisma","Prisma"),("typeorm","TypeORM"),("mongoose","Mongoose"),("sqlalchemy","SQLAlchemy")]
    t = text.lower()
    for k,v in checks:
        if k in t or k in " ".join(paths).lower(): found.append(v)
    return list(dict.fromkeys(found))


def _auth(text) -> list[str]:
    found = []
    t = text.lower()
    checks = [("jwt","JWT"),("oauth","OAuth"),("passport","Passport.js"),("nextauth","NextAuth"),("auth0","Auth0"),("firebase auth","Firebase Auth"),("clerk","Clerk"),("supabase auth","Supabase Auth"),("session","Session-based"),("api key","API Key"),("bearer","Bearer Token")]
    for k,v in checks:
        if k in t: found.append(v)
    return list(dict.fromkeys(found))


def _patterns(paths, text) -> list[str]:
    found = []
    t = text.lower()
    p = " ".join(paths).lower()
    checks = [("repository","Repository Pattern"),("singleton","Singleton"),("factory","Factory"),("observer","Observer"),("middleware","Middleware"),("mvc","MVC"),("mvvm","MVVM"),("restful","REST"),("graphql","GraphQL"),("event","Event-Driven"),("cqrs","CQRS"),("pub/sub","Pub/Sub")]
    for k,v in checks:
        if k in t or k in p: found.append(v)
    return list(dict.fromkeys(found))


def _pkg_managers(paths) -> list[str]:
    found = []
    p = " ".join(paths)
    if "package-lock.json" in p: found.append("npm")
    if "yarn.lock" in p: found.append("yarn")
    if "pnpm-lock.yaml" in p: found.append("pnpm")
    if "requirements.txt" in p or "pyproject.toml" in p: found.append("pip")
    if "Pipfile" in p: found.append("pipenv")
    if "poetry.lock" in p: found.append("poetry")
    if "go.sum" in p: found.append("go modules")
    if "Cargo.toml" in p: found.append("cargo")
    if "Gemfile" in p: found.append("bundler")
    return found


def _deployment(paths) -> list[str]:
    found = []
    p = " ".join(paths).lower()
    checks = [("dockerfile","Docker"),("docker-compose","Docker Compose"),("kubernetes","Kubernetes"),(".github/workflows","GitHub Actions"),("vercel.json","Vercel"),("netlify","Netlify"),("render.yaml","Render"),("heroku","Heroku"),("terraform","Terraform"),("serverless.yml","Serverless Framework"),("cloudbuild","Google Cloud Build")]
    for k,v in checks:
        if k in p: found.append(v)
    return list(dict.fromkeys(found))
