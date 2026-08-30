#!/usr/bin/env python3
"""
Batch-check whether things a doc claims about the code actually exist.

Every run of this skill otherwise reinvents the same grep loop: "the doc says
there's no such model / no such route / no such module — is that true?"
Doing it by hand is slow and inconsistent, and inconsistency is what produces
a delete list where some rows are solid and some are guesses.

This gives you one cheap, uniform existence check so the expensive reading
time goes to the claims that actually need judgement.

Feed it the nouns a doc asserts (or denies) and it tells you which ones the
code actually contains.

Usage:
    python verify_claims.py <repo> --symbols SomeService SomeGuard
    python verify_claims.py <repo> --paths src/thing/thing.controller.ts
    python verify_claims.py <repo> --routes /v1/resource admin/other-resource
    python verify_claims.py <repo> --models SomeModel AnotherModel
    echo '{"symbols":["SomeService"],"routes":["/v1/resource"]}' | python verify_claims.py <repo> --stdin

Output: JSON, one verdict per claim.
    {"kind":"symbol","claim":"SomeService","exists":true,
     "evidence_strength":"declaration",
     "hits":[{"file":"src/thing/some.service.ts","line":12,"text":"..."}],
     "hit_count":3}

EXISTENCE IS NOT CORRECTNESS. A hit proves the name appears, not that the
feature is complete or wired up. Treat `exists: true` as "the doc's negative
claim is refuted" and `exists: false` as "worth reading before you act" — a
miss can just mean the doc used different wording than the code.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CODE_GLOBS = [
    "*.ts", "*.tsx", "*.js", "*.jsx", "*.py", "*.go", "*.rs",
    "*.java", "*.rb", "*.php", "*.prisma", "*.sql", "*.yaml", "*.yml",
]
EXCLUDE_DIRS = [
    "node_modules", ".git", "dist", "build", "out", "coverage",
    ".next", ".turbo", "vendor", "__pycache__", ".venv",
]
MAX_HITS = 6


def ripgrep(repo: Path, pattern: str, globs: list[str] | None = None) -> list[dict]:
    """Prefer ripgrep; fall back to git grep so this works on a bare toolchain."""
    globs = globs or CODE_GLOBS
    cmd = ["rg", "--json", "-i", pattern, str(repo)]
    for d in EXCLUDE_DIRS:
        cmd += ["-g", f"!{d}/**"]
    for g in globs:
        cmd += ["-g", g]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        hits = []
        for line in out.stdout.splitlines():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") != "match":
                continue
            d = ev["data"]
            hits.append({
                "file": str(Path(d["path"]["text"]).relative_to(repo)),
                "line": d["line_number"],
                "text": d["lines"]["text"].strip()[:200],
            })
            if len(hits) >= MAX_HITS:
                break
        return hits
    except FileNotFoundError:
        pass
    except (subprocess.SubprocessError, OSError, ValueError):
        return []

    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "grep", "-n", "-I", "-i", "-E", pattern],
            capture_output=True, text=True, timeout=60,
        )
        hits = []
        for line in out.stdout.splitlines()[:MAX_HITS]:
            parts = line.split(":", 2)
            if len(parts) == 3:
                hits.append({"file": parts[0], "line": int(parts[1]),
                             "text": parts[2].strip()[:200]})
        return hits
    except (subprocess.SubprocessError, OSError, ValueError):
        return []


def check_symbol(repo: Path, name: str) -> dict:
    """Require a declaration, not a passing mention — a doc naming a symbol in
    prose shouldn't count as evidence that the symbol exists."""
    pat = (rf"\b(class|interface|enum|type|model|const|function|def|struct)\s+{re.escape(name)}\b"
           rf"|\b{re.escape(name)}\s*=\s*(class|function|\()")
    hits = ripgrep(repo, pat)
    if not hits:  # fall back to any mention, flagged as weaker evidence
        hits = ripgrep(repo, rf"\b{re.escape(name)}\b")
        return {"kind": "symbol", "claim": name, "exists": bool(hits),
                "evidence_strength": "mention_only" if hits else "none",
                "hits": hits, "hit_count": len(hits)}
    return {"kind": "symbol", "claim": name, "exists": True,
            "evidence_strength": "declaration", "hits": hits, "hit_count": len(hits)}


def check_path(repo: Path, rel: str) -> dict:
    p = (repo / rel.lstrip("./"))
    if p.exists():
        return {"kind": "path", "claim": rel, "exists": True,
                "evidence_strength": "exact", "hits": [{"file": rel, "line": 0, "text": "exists"}],
                "hit_count": 1}
    matches = [str(m.relative_to(repo)) for m in repo.rglob(Path(rel).name)
               if not any(d in m.parts for d in EXCLUDE_DIRS)][:MAX_HITS]
    return {"kind": "path", "claim": rel, "exists": bool(matches),
            "evidence_strength": "moved" if matches else "none",
            "hits": [{"file": m, "line": 0, "text": "same filename, different path"} for m in matches],
            "hit_count": len(matches)}


def check_route(repo: Path, route: str) -> dict:
    """Routes are usually split across a controller prefix and a method
    decorator, so match the distinctive segments rather than the whole path."""
    segs = [s for s in route.strip("/").split("/") if s and not s.startswith(":") and "{" not in s]
    if not segs:
        return {"kind": "route", "claim": route, "exists": False,
                "evidence_strength": "none", "hits": [], "hit_count": 0}
    pat = "|".join(re.escape(s) for s in segs[-2:])
    hits = ripgrep(repo, rf"['\"`/]({pat})['\"`/]")
    return {"kind": "route", "claim": route, "exists": bool(hits),
            "evidence_strength": "segment_match" if hits else "none",
            "hits": hits, "hit_count": len(hits)}


def check_model(repo: Path, name: str) -> dict:
    hits = ripgrep(repo, rf"^\s*(model|type|table)\s+{re.escape(name)}\b",
                   globs=["*.prisma", "*.sql", "*.ts", "*.py"])
    return {"kind": "model", "claim": name, "exists": bool(hits),
            "evidence_strength": "declaration" if hits else "none",
            "hits": hits, "hit_count": len(hits)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Check whether doc claims about code hold.")
    ap.add_argument("repo")
    ap.add_argument("--symbols", nargs="*", default=[])
    ap.add_argument("--paths", nargs="*", default=[])
    ap.add_argument("--routes", nargs="*", default=[])
    ap.add_argument("--models", nargs="*", default=[])
    ap.add_argument("--stdin", action="store_true", help="Read a JSON claim bundle from stdin")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(json.dumps({"error": f"not a directory: {repo}"}))
        return 1

    symbols, paths, routes, models = args.symbols, args.paths, args.routes, args.models
    if args.stdin:
        try:
            b = json.load(sys.stdin)
            symbols += b.get("symbols", []); paths += b.get("paths", [])
            routes += b.get("routes", []); models += b.get("models", [])
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"bad stdin JSON: {e}"}))
            return 1

    results = (
        [check_symbol(repo, s) for s in symbols]
        + [check_path(repo, p) for p in paths]
        + [check_route(repo, r) for r in routes]
        + [check_model(repo, m) for m in models]
    )

    found = sum(1 for r in results if r["exists"])
    json.dump({
        "repo": str(repo),
        "checked": len(results),
        "found": found,
        "missing": len(results) - found,
        "results": results,
        "caveat": "Existence is not correctness. A hit refutes a doc's negative "
                  "claim; it does not prove the feature is complete or wired up.",
    }, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
