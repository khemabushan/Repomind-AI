"""Clone a GitHub repo into a temp directory and walk the file tree."""
import os, shutil
from pathlib import Path
from git import Repo as GitRepo
from app.core.config import settings

import subprocess
import os
import shutil

SKIP_DIRS = {".git","node_modules","__pycache__",".venv","venv","dist","build",".next",".nuxt","coverage",".pytest_cache"}
SKIP_EXTS = {".png",".jpg",".jpeg",".gif",".svg",".ico",".woff",".woff2",".ttf",".eot",".mp4",".mp3",".zip",".tar",".gz"}
TEXT_EXTS  = {".py",".js",".ts",".tsx",".jsx",".java",".go",".rs",".rb",".php",".cs",".cpp",".c",".h",".swift",".kt",".scala",".html",".css",".scss",".less",".sql",".sh",".bash",".yaml",".yml",".json",".toml",".md",".txt",".xml",".graphql",".prisma",".tf"}


def clone_repo(url: str, repo_id: str) -> str:
    dest = os.path.join(settings.repo_clone_dir, repo_id)

    if os.path.exists(dest):
        shutil.rmtree(dest)

    os.makedirs(settings.repo_clone_dir, exist_ok=True)

    subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "clone",
            "--depth",
            "1",
            url,
            dest,
        ],
        check=True,
    )

    return dest

def walk_repo(root: str) -> list[dict]:
    files = []
    root_path = Path(root)
    for p in root_path.rglob("*"):
        if p.is_dir(): continue
        parts = p.relative_to(root_path).parts
        if any(pt.startswith(".") or pt in SKIP_DIRS for pt in parts): continue
        if p.suffix.lower() in SKIP_EXTS: continue
        if p.suffix.lower() not in TEXT_EXTS and p.suffix != "": continue
        try:
            if p.stat().st_size > 200_000: continue
            files.append({"path": str(p.relative_to(root_path)), "content": p.read_text(encoding="utf-8",errors="replace"), "language": _lang(p.suffix.lower()), "size": p.stat().st_size})
        except Exception: continue
    return files

def _lang(ext: str) -> str:
    M={".py":"Python",".js":"JavaScript",".ts":"TypeScript",".tsx":"TypeScript",".jsx":"JavaScript",".java":"Java",".go":"Go",".rs":"Rust",".rb":"Ruby",".php":"PHP",".cs":"C#",".cpp":"C++",".c":"C",".swift":"Swift",".kt":"Kotlin",".scala":"Scala",".html":"HTML",".css":"CSS",".scss":"SCSS",".sql":"SQL",".sh":"Shell",".yaml":"YAML",".yml":"YAML",".json":"JSON",".md":"Markdown",".tf":"Terraform"}
    return M.get(ext,"Text")

def count_loc(files: list[dict]) -> int:
    return sum(f["content"].count("\n") for f in files)
