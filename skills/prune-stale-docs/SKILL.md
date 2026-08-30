---
name: prune-stale-docs
description: Find and remove documentation that has become false — resolved bug/audit reports, "not built yet" claims about things that shipped, completed-work history sections, and references to code that no longer exists. Stale docs are read by AI agents as current fact and silently corrupt their reasoning, so use this skill whenever the user mentions outdated/stale/rotten docs, doc cleanup or hygiene, docs that "confuse the AI" or "poison the agents", or says the docs no longer match the code. Also reach for it proactively right after a big remediation, refactor, or feature push — the moment work lands is the moment its planning and audit docs become lies. Trigger even when the user only says something vague like "these docs are out of date" or "should we delete this old audit?".
---

# Prune stale docs

## Why this matters

A stale document is worse than no document. Humans skim and discount old text; agents don't. An agent reading `docs/` treats present-tense statements as ground truth and acts on them.

The characteristic failure: an agent is asked to audit a system, reads a months-old status line saying a capability is blocked or missing, and reports it as a live finding. The capability shipped weeks ago. One stale line propagates into a deliverable as fact, and nobody catches it because the doc *looked* authoritative.

That's what you're preventing: **documents that assert a state the code no longer has.**

## The one rule that keeps this safe

**A claim is stale only if the code contradicts it — never because it looks old.**

Everything here hinges on verification. You are not pattern-matching for suspicious words and deleting; you are finding claims, checking them against the repository, and removing only what is demonstrably false.

This matters most for plans and roadmaps. Aspirational statements ("we will add rate limiting") are intent, not rot — they don't expire. Only the *status* attached to them can go stale, and only when the thing actually shipped. A roadmap item marked "not started" for something genuinely not started is correct and stays.

## Where things belong

When deciding delete-vs-keep, apply this split:

- **Repo docs answer "what is true now?"** — present-tense descriptions of how the system works.
- **Version control answers "what was true then?"** — deleted docs remain in history, retrievable forever.
- **Code comments answer "why is it like this?"** — the durable, valuable residue of a fixed bug.

So deleting a fully-remediated audit usually loses nothing. But if reasoning worth keeping exists *only* in the doc you're about to delete, move it into a code comment first. That's a real loss to prevent, and it's cheap.

## Workflow

### 0. Start where the blast radius is largest

Before any broad sweep, check the files agents load on *every* task. Depending on the toolchain these include `CLAUDE.md`, `AGENTS.md`, `.claude/**`, `.cursorrules`, `.github/copilot-instructions.md`, `CONTRIBUTING`, the root `README`, and any per-directory instruction file sitting beside code.

A wrong line here is read on every single task; a wrong line in an obscure design doc might never be read at all. These files are also reliably among the *most* rotted, because teams treat them as configuration rather than documentation and never review them.

Typical rot found here: a stated framework or dependency version that's since been upgraded; commands using the wrong package manager; a described architecture pattern the codebase has since abandoned or explicitly banned; a claim that some category of code "doesn't exist yet" when the tree is full of it.

Fixing these is fast, requires no deletion, and often removes more agent confusion than the entire rest of the cleanup. Do it first and report it separately.

### 1. Scope

Establish which docs are in play. Default to version-controlled markdown. Ask the user when scope is ambiguous — one repo or several, include the README, is there a sibling repo whose docs live here?

Run the scanner to narrow the field:

```bash
python scripts/scan_docs.py <repo-path> [<repo-path> ...] [--exclude <glob> ...]
```

It emits JSON: candidate files, flagged lines with their staleness signal, and cited code paths that no longer resolve. It deliberately makes no judgement — it tells you where to look so your attention goes to verification instead of grepping.

**Exclude generated output explicitly, and say that you did.** Any directory of machine-written markdown — static-site build output, API reference generators, tooling report snapshots, dated export folders — will dominate a scan and is regenerated rather than maintained. Reviewing it is wasted effort and deleting it is pointless. The scanner skips common cases and takes `--exclude` for whatever this repo happens to use.

### 2. Detect

Four categories are worth acting on. The scanner surfaces candidates; you confirm.

**a. Resolved problem documents.** Whole files whose reason to exist was describing something wrong: audits, gap analyses, remediation plans, postmortems, migration plans for a completed migration. Signal: the document's own framing is "here is what's broken."

**b. Stale status claims inside living docs.** Lines asserting current state — "X is disabled", "no such module exists", "this isn't built yet", "currently returns an error", "❌ not started", "blocked on Y". These are the highest-value catches: they read as fact and sit inside documents that are otherwise correct and actively consulted.

**c. Completed-work history sections.** "Recently completed", "Shipped", "Done in v2" — changelog-shaped lists inside a status or planning document. This is history wearing a status doc's costume, and it's a common source of the failure described above. Version control already holds it.

**d. Dead code references.** Paths, symbols, endpoints, or config keys the doc cites that no longer exist. These waste agent time and imply structure that isn't there.

### 3. Verify — the crux

For every candidate, find evidence in the repository. Never rely on a document's claim about itself.

**Batch the cheap checks first.** Most claims reduce to "does this thing exist?" — a model, module, route, symbol, or file. Collect them across all candidates and settle them in one pass:

```bash
python scripts/verify_claims.py <repo> --symbols Foo Bar --models Baz --routes /v1/thing --paths src/x/y.ts
```

Each verdict carries an `evidence_strength` (`declaration` > `mention_only` > `none`). Heed its caveat: existence refutes a doc's *negative* claim, but does not prove a feature is complete or wired up. "The model exists" and "the feature works" are different findings.

**Never trust a document's own status banner or checkboxes.** A file headed `status: draft — awaiting review` may contain a close-out note further down saying it shipped. A "✅ verified accurate" stamp may be a year stale. Plans routinely sit at zero ticked boxes long after every line shipped, because nobody returns to tick them. Banners and checkboxes are claims like any other and get checked against code like any other.

This matters doubly if you're about to *recommend* status banners as the fix: stamping a false document "verified" is the worst available outcome — strictly worse than leaving it alone, and much worse than deleting it.

**Spend effort where it pays.** Exhaustively verifying every document costs hours and mostly re-confirms that obscure files are still obscure. Triage:

1. **Verify in full:** agent entry points, and anything you intend to DELETE. A wrong delete is the expensive mistake.
2. **Verify representatively:** large uniform clusters — a directory of plans all following one template. Check several closely, confirm the pattern holds, then state the sampling plainly rather than implying you read them all.
3. **Flag, don't chase:** the long tail nobody loads. Note them as low-priority; don't burn the budget there.

Parallel subagents help on large repos — one per document cluster, since verification is independent read-only work. But prefer one good batch check over several agents running overlapping greps.

If you cannot verify a claim either way, **leave it and say so.** Uncertain is not stale.

### 3b. Track what you could NOT verify

Verification has edges, and hiding them turns a cleanup proposal into a liability. Keep a running list of:

- **Cross-repo claims** — a doc describing a client, service, or package whose source you can't read. You can confirm the doc exists; you cannot confirm it's current.
- **Sampling** — if you checked 5 of 18 and inferred the rest, that's a real distinction. Say so, and hand over the cheap check that would settle it.
- **External state** — anything whose truth lives outside the repo: a vendor's approval status, an account's billing state, whether CI is actually running.

Then **never write "every claim was verified"** unless it is literally true. Someone reading a long delete list has no way to tell which rows are solid and which are thin — that calibration is the most valuable thing you can give them, and overclaiming destroys it.

### 4. Classify

| Disposition | When |
|---|---|
| **DELETE** | Whole file, fully obsolete, reasoning worth keeping already lives in code or history |
| **PRUNE** | Doc is alive; specific sections are false — cut them, keep the rest |
| **UPDATE** | Claim is false but the topic still needs a statement — rewrite to current truth |
| **KEEP** | Verified accurate, genuinely aspirational, or unverifiable |

Prefer PRUNE/UPDATE over DELETE when a document has ongoing value. Deletion is for files whose entire reason to exist has passed.

### 5. Propose, then act

Present the plan and wait for approval before writing anything. Deletion is irreversible outside version control, and the user knows which docs carry contractual, compliance, or onboarding weight that the code can't reveal.

Every row carries a **confidence label**, because a long delete list mixing checked and inferred rows is unreviewable without one:

- `[verified]` — you read the contradicting code yourself.
- `[inferred]` — matches a pattern you confirmed on siblings; you didn't open this one.
- `[unverified]` — depends on something you can't see.

```
## Proposed changes
Verified N of M claims directly; K inferred from confirmed patterns; J unverifiable.

### DELETE (N files)
- [verified] `path/to/doc.md` — <what it was for, why it's done>
  Evidence: <the specific thing you checked and found>

### PRUNE (N files)
- [verified] `path/to/doc.md` §4.2 — "<the false claim, quoted>"
  Evidence: <the code that contradicts it>

### UPDATE (N files)
- [verified] `path/to/doc.md:67` — "<false claim>" → "<current truth>"
  Evidence: <...>

### KEEP
- `path/to/doc.md` — <why it survived: accurate / aspirational / unverifiable>

### Could not verify
- `path/to/doc.md` — <why: other repo / sampled / external state>
  How to check: <the cheap command that would settle it>
```

Quote the offending text and cite the contradicting code. A reader should be able to sanity-check any single row in seconds without opening a file, and see at a glance which rows are safe to accept wholesale.

After approval, make the edits surgically, then confirm what changed and note that deleted files remain recoverable from history.

**Findings beyond the docs outrank the cleanup.** Verification means reading code against claims — exactly the activity that surfaces real defects: a column dropped by a migration but still read in a service, a doc describing a table a later migration removed, a fixed vulnerability still written up as open. When you find one, lead with it. Owners care more about a live bug than about which markdown files you'd delete.

### 6. Say why it rotted

Deletion treats the symptom. If a repo has hundreds of unticked boxes across shipped plans, or several competing "plans" directories, or most docs unreachable except by an agent globbing a folder, then it has a *process* problem and the same mess returns in months.

Close with a short paragraph on the mechanism and the cheapest habit that prevents recurrence — one designated status-bearing doc, plans archived on merge, generated output gitignored. Owners consistently find this more useful than the file list, and it costs a few sentences.

## Safety rails

The cost of a wrong delete far exceeds the cost of a missed stale line.

- **Check version-control state first.** An untracked or uncommitted file has no safety net — call that out and get explicit confirmation before deleting. Prefer working from a clean tree.
- **Never delete files whose job is to be historical.** Changelogs, licenses, architecture decision records, release notes, migrations, anything under an archive path. Their "staleness" is the point.
- **Treat entry-point and agent-instruction files as prune-only.** Deleting one is a far bigger change than fixing its wrong lines — and its wrong lines are the highest-impact thing you'll fix all session.
- **Rescue the "why" before deleting.** If a doc holds reasoning captured nowhere else, propose moving it into a code comment as part of the same change.
- **Stay in scope and don't improve prose while you're in there.** Surgical edits keep the diff reviewable.
- **A published contract** — an API reference a third party consumes — can be corrected freely, but deleting it needs a deliberate decision from the user.

## Handling disagreement about deletion

Users often want to keep a remediated audit as a record of diligence. That's legitimate. The workable compromise is to keep the file but make its status unmissable at the very top — a clear resolved banner with a date — so no agent reads its body as current.

What doesn't work is leaving a resolved audit's findings in present tense with a note buried at the bottom. Agents read top-down and frequently stop early.

## Good and bad calls

**Good catch.** A spec says *"no audit-logging exists — this is a known gap."* Verification finds the model, the module, and its use across a dozen call sites. → **UPDATE** to describe what shipped, and note the narrower gap that genuinely remains.

**Good catch.** A roadmap carries a long "Recently completed" section listing shipped items. Verified present. → **PRUNE** the section; a roadmap should hold open work, and history lives in version control.

**Bad call.** Deleting a roadmap line reading *"❌ error tracking not integrated"* because it sounds negative. Verification finds no error-tracking anywhere. The claim is **true** — that's open work, not rot. → **KEEP**.

**Bad call.** Deleting an architecture doc because it describes a workaround for a bug. The workaround is still in the code. → **KEEP**; it explains current reality.

**Bad call.** Stamping a doc "✅ verified" based on its own existing banner. Banners are claims; check them or don't touch them.

## When you're done

Report tersely: files deleted, sections pruned, claims corrected, and anything deliberately left with the reason. If you found a doc claiming something shipped that hasn't — or a live code defect — surface that first. It's usually more valuable than the cleanup itself.
