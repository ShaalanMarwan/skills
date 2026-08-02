# Shaalan's Skills

A growing collection of practical, source-backed skills for coding agents.

The repository works as a single plugin for Codex and Claude Code while keeping every skill isolated under `skills/<skill-name>/`. Skills can therefore be used together or copied independently.

## Skills

### `drift-flutter`

Design, implement, migrate, test, and debug Drift databases in Flutter applications. It covers schema design, generated APIs, reactive queries, platform setup, migrations, isolates, testing, synchronization boundaries, and common failure modes.

The guidance was built from a complete audit of the official Drift documentation and checked against the Drift source repository.

## Repository structure

```text
.
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
└── skills/
    └── drift-flutter/
        ├── SKILL.md
        ├── agents/
        └── references/
```

Future skills belong in their own directories under `skills/`.

## Install

### Skills CLI

```bash
npx skills@latest add ShaalanMarwan/skills
```

### Claude Code

Add this repository as a plugin marketplace and install `shaalan-skills` from it. The repository includes a Claude Code plugin manifest at `.claude-plugin/plugin.json`.

### Codex

The repository includes a native Codex manifest at `.codex-plugin/plugin.json`. It can also be installed through the Skills CLI command above.

## Sources

- [Drift documentation](https://drift.simonbinder.eu/)
- [Drift source repository](https://github.com/simolus3/drift)

## License

MIT
