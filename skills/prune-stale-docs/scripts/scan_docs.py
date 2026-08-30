#!/usr/bin/env python3
"""
Narrow the search space for stale documentation.

This script finds *candidates* — it deliberately makes no judgement about
whether anything is actually stale. That call requires reading the code, which
is the agent's job. What this does is the mechanical part that would otherwise
be re-invented on every run: enumerate tracked docs, flag lines carrying a
staleness signal, and check whether the code references docs cite still resolve.

Usage:
    python scan_docs.py <repo-path> [<repo-path> ...] [--json] [--all-files]

Output: JSON to stdout.
    {
      "repos": [{
        "repo": "/path",
        "clean_tree": true,
        "docs": [{
          "path": "docs/FOO.md",
          "tracked": true,
          "dirty": false,
          "protected": false,          # historical-by-design; never delete
          "entry_point": false,        # README/CLAUDE.md/AGENTS.md; prune-only
          "whole_file_signals": [...], # suggests the file's purpose is "describe a problem"
          "flagged_lines": [{"line": 67, "signal": "status_claim", "text": "..."}],
          "dead_refs": [{"line": 12, "ref": "src/gone.ts", "kind": "path"}]
        }]
      }]
    }
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# --- What never gets deleted -------------------------------------------------
# These are historical by design. Their staleness is the entire point, so
# flagging them as rot would be a category error.
PROTECTED_PATTERNS = [
    r"(^|/)CHANGELOG",
    r"(^|/)LICEN[CS]E",
    r"(^|/)HISTORY",
    r"(^|/)RELEASE[-_ ]?NOTES",
    r"(^|/)(docs/)?(adr|decisions|rfcs?)/",
    r"(^|/)(archive|history|legacy)/",
    r"(^|/)migrations?/",
    r"(^|/)node_modules/",
    r"(^|/)vendor/",
    r"(^|/)\.git/",
    r"(^|/)(dist|build|out|coverage)/",
]

# Machine-written markdown. It regenerates rather than rots, so reviewing it is
# wasted effort — and on a large repo it will otherwise swamp the candidate list.
# These cover common generators; every repo has its own tooling, so pass
# --exclude for anything project-specific rather than editing this list.
GENERATED_PATTERNS = [
    r"(^|/)\.docusaurus/",
    r"(^|/)_?site/",
    r"(^|/)storybook-static/",
    r"(^|/)typedoc/",
    r"(^|/)(api-)?docs?/generated/",
    r"(^|/)generated/",
    r"(^|/)\.vitepress/dist/",
    r"(^|/)target/doc/",
    r"(^|/)\d{4}-\d{2}-\d{2}/",  # dated report/export snapshots
]

# Entry points: agents read these on essentially every task, so a stale line
# here is maximally damaging — but deleting the file is far too blunt.
ENTRY_POINT_PATTERNS = [
    r"^README",                     # root README only — nested ones are ordinary docs
    r"^CONTRIBUTING",
    r"(^|/)CLAUDE[-.][\w-]*\.md$",  # CLAUDE.md, CLAUDE-architecture.md, CLAUDE-tests.md
    r"(^|/)AGENTS\.md$",
    r"^\.claude/",                  # everything an agent auto-loads
    r"^\.cursor(rules)?",
    r"(^|/)\.github/copilot-instructions\.md$",
]

# --- Line-level staleness signals --------------------------------------------
# Each is a claim *about current state*. That's what makes them dangerous: an
# agent reads them as fact. Aspirational language ("we should", "we plan to")
# is intentionally NOT matched — intent doesn't go stale, status does.
LINE_SIGNALS: list[tuple[str, str]] = [
    (
        "status_claim",
        r"\b(is|are|remains?|currently)\s+"
        r"(rejected|unsubmitted|not\s+live|not\s+enabled|disabled|blocked|broken|failing|missing|pending)\b",
    ),
    (
        "negative_existence",
        r"\b(no|there\s+is\s+no|there\s+are\s+no|does\s+not|doesn't|don't)\s+"
        r"\w*\s*(exist|exists|implemented|support|endpoint|route|model|module|table|handler)\b",
    ),
    (
        "not_built_yet",
        r"\b(not\s+(yet\s+)?(built|implemented|started|wired|shipped|done|deployed|integrated)"
        r"|no\s+\w+\s+yet|yet\s+to\s+be\s+(built|implemented)|still\s+(a\s+)?(stub|todo|pending))\b",
    ),
    (
        "status_marker",
        r"(❌|🔴|⛔)|\b(TODO|FIXME|BLOCKER|BLOCKED\s+ON)\b|\*\*(not\s+started|planned|unbuilt)\*\*",
    ),
    (
        "completed_marker",
        r"(✅|🟢|✔)|\b(shipped|completed|done|resolved|fixed|remediated|landed)\b",
    ),
    (
        "stub_claim",
        r"\b(stub|placeholder|mock(ed)?|fake|dummy|hard-?coded)\b.{0,40}\b(today|for\s+now|currently|until)\b"
        r"|\b(returns?|responds?\s+with)\s+50[13]\b",
    ),
    (
        "temporal_claim",
        r"\b(as\s+of|currently|at\s+the\s+moment|right\s+now|today|at\s+time\s+of\s+writing)\b",
    ),
]

# --- Whole-file signals ------------------------------------------------------
# Suggests the document's reason to exist is "describe something wrong" — the
# class of doc that becomes pure noise once the problem is fixed.
WHOLE_FILE_SIGNALS: list[tuple[str, str]] = [
    ("audit_doc", r"\b(audit|assessment|readiness\s+review)\b"),
    ("problem_doc", r"\b(gap\s+analysis|findings|remediation|postmortem|post-mortem|incident)\b"),
    ("severity_language", r"\b(critical|blocker|vulnerabilit(y|ies)|must[- ]fix)\b"),
    ("plan_doc", r"\b(migration\s+plan|rollout\s+plan|remediation\s+plan|action\s+plan)\b"),
    ("resolved_banner", r"\b(resolved|all\s+fixed|fully\s+remediated|no\s+longer\s+applies|superseded)\b"),
]

# Code references worth existence-checking. Docs cite paths in backticks
# constantly; a path that no longer resolves is a concrete, checkable defect.
PATH_REF = re.compile(r"`([\w./-]+\.(?:ts|tsx|js|jsx|py|go|rs|java|rb|php|prisma|sql|ya?ml|json|toml|sh))`")

MAX_LINE_ECHO = 220


def run_git(repo: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, timeout=30,
        )
        return out.stdout if out.returncode == 0 else None
    except (subprocess.SubprocessError, OSError):
        return None


def list_docs(repo: Path, all_files: bool) -> list[str]:
    """Prefer git-tracked files: untracked docs have no safety net, and the
    agent needs to know the difference before proposing a delete."""
    if not all_files:
        tracked = run_git(repo, "ls-files", "*.md", "*.mdx")
        if tracked is not None:
            return [p for p in tracked.splitlines() if p.strip()]
    return [
        str(p.relative_to(repo))
        for p in repo.rglob("*.md")
        if not any(re.search(pat, str(p.relative_to(repo)), re.I) for pat in PROTECTED_PATTERNS[-5:])
    ]


def dirty_files(repo: Path) -> set[str]:
    status = run_git(repo, "status", "--porcelain")
    if status is None:
        return set()
    out = set()
    for line in status.splitlines():
        if len(line) > 3:
            out.add(line[3:].strip().split(" -> ")[-1])
    return out


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(re.search(p, path, re.I) for p in patterns)


IGNORED_DIRS = {
    "node_modules", ".git", "dist", "build", "out", "coverage",
    ".next", ".turbo", "vendor", "__pycache__", ".venv", "venv", "generated",
}


def build_file_index(repo: Path) -> tuple[set[str], set[str]]:
    """Index the repo once: (relative paths, bare filenames).

    Docs cite paths loosely — sometimes `src/foo/bar.ts`, sometimes just
    `bar.ts` — so a reference counts as live if either form resolves. Building
    this once turns the dead-ref check from a per-reference filesystem walk
    into a set lookup, which is the difference between seconds and minutes on
    a repo with dependencies installed.
    """
    rels: set[str] = set()
    names: set[str] = set()
    tracked = run_git(repo, "ls-files")
    if tracked:
        for p in tracked.splitlines():
            p = p.strip()
            if p:
                rels.add(p)
                names.add(Path(p).name)
        return rels, names

    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        for f in files:
            full = Path(root) / f
            try:
                rels.add(str(full.relative_to(repo)))
            except ValueError:
                continue
            names.add(f)
    return rels, names


def scan_file(repo: Path, rel: str, index: tuple[set[str], set[str]]) -> dict | None:
    full = repo / rel
    try:
        text = full.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeError):
        return None

    lines = text.splitlines()
    head = "\n".join(lines[:60])  # framing lives near the top

    whole = [name for name, pat in WHOLE_FILE_SIGNALS if re.search(pat, head, re.I)]

    flagged, dead = [], []
    in_fence = False
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue  # code samples aren't claims about the world

        for name, pat in LINE_SIGNALS:
            if re.search(pat, line, re.I):
                flagged.append({
                    "line": i,
                    "signal": name,
                    "text": line.strip()[:MAX_LINE_ECHO],
                })
                break

        rel_paths, bare_names = index
        for m in PATH_REF.finditer(line):
            ref = m.group(1)
            if ref.startswith(("http", "//")):
                continue
            norm = ref.lstrip("./")
            resolves = (
                norm in rel_paths
                or Path(ref).name in bare_names
                or (repo / norm).exists()
                or any(p.endswith("/" + norm) for p in rel_paths)
            )
            if not resolves:
                dead.append({"line": i, "ref": ref, "kind": "path"})

    if not (whole or flagged or dead):
        return None

    return {
        "path": rel,
        "protected": matches_any(rel, PROTECTED_PATTERNS),
        "entry_point": matches_any(rel, ENTRY_POINT_PATTERNS),
        "lines_total": len(lines),
        "whole_file_signals": whole,
        "flagged_lines": flagged,
        "dead_refs": dead,
    }


def scan_repo(repo_path: str, all_files: bool, extra_excludes: list[str] | None = None) -> dict:
    repo = Path(repo_path).resolve()
    if not repo.is_dir():
        return {"repo": str(repo), "error": "not a directory"}

    dirty = dirty_files(repo)
    is_git = run_git(repo, "rev-parse", "--git-dir") is not None

    index = build_file_index(repo)

    docs, generated_skipped = [], 0
    for rel in list_docs(repo, all_files):
        if matches_any(rel, GENERATED_PATTERNS + (extra_excludes or [])):
            generated_skipped += 1
            continue
        entry = scan_file(repo, rel, index)
        if entry:
            entry["tracked"] = is_git and rel not in dirty or rel not in dirty
            entry["dirty"] = rel in dirty
            docs.append(entry)

    # Entry points first: a wrong line in CLAUDE.md is read on every task,
    # while a wrong line in an obscure design doc may never be read at all.
    def weight(d: dict) -> int:
        return (
            len(d["whole_file_signals"]) * 3
            + len(d["flagged_lines"])
            + len(d["dead_refs"])
        )

    # Entry points that actually carry a signal come first — a wrong line in
    # CLAUDE.md is read on every task. An entry point with nothing flagged is
    # just a clean file and shouldn't outrank a doc with 160 suspect lines.
    docs.sort(key=lambda d: (d["entry_point"] and weight(d) > 0, weight(d)), reverse=True)

    return {
        "repo": str(repo),
        "is_git_repo": is_git,
        "clean_tree": is_git and not dirty,
        "docs_with_candidates": len(docs),
        "generated_files_skipped": generated_skipped,
        "docs": docs,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Find candidate stale docs (does not judge).")
    ap.add_argument("repos", nargs="+", help="Repository paths to scan")
    ap.add_argument("--all-files", action="store_true",
                    help="Include untracked docs (default: git-tracked only)")
    ap.add_argument("--exclude", nargs="*", default=[], metavar="REGEX",
                    help="Extra path patterns to skip, e.g. project-specific "
                         "generated-output directories")
    args = ap.parse_args()

    result = {"repos": [scan_repo(r, args.all_files, args.exclude) for r in args.repos]}
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")

    total = sum(r.get("docs_with_candidates", 0) for r in result["repos"])
    print(
        f"\n{total} document(s) have candidates. "
        "Nothing here is confirmed stale — verify each claim against the code before proposing changes.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
