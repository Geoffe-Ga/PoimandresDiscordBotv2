# Claude Code Project Context: Poimandres Discord Bot

**Version**: 1.0
**Last Updated**: 2026-05-22
**Status**: Mid-migration — Node.js (`discord.js` v13) → Python (`discord.py` 2.x)

---

## Quick Navigation

- **Build spec**: [`plans/python-recreation-prompt.md`](plans/python-recreation-prompt.md) — the exhaustive, authoritative specification for the Python bot. Build exactly what it describes.
- **Skills**: [`.claude/skills/`](.claude/skills/) — 25 well-worn-tools skills (stay-green, testing, security, etc.). Claude loads these automatically when relevant.
- **Original source**: `index.js`, `commands/`, `deploy-commands.js`, `server-count.js` — the Node.js bot being replaced. Read it as reference, do not extend it.

---

## Critical Principles

1. **The spec is law.** `plans/python-recreation-prompt.md` defines the target bot exactly. Build what it says; do not add features it does not describe.
2. **Text corpora are sacred.** The ~6 MB of public-domain scripture in `commands/books/*.json` must be carried over **verbatim**. Never paraphrase, re-key, regenerate, or "clean up" passage text.
3. **Stay Green.** Never commit or request review with failing tests or quality checks. Red → Green → Refactor (see the `stay-green` skill).
4. **No shortcuts — fix root causes.** Never bypass linters or type checkers with `# noqa`, `# type: ignore`, etc. without a justified, issue-referenced reason (see `max-quality-no-shortcuts`).
5. **No committed secrets.** The Discord token, application/client ID, and dev guild ID come from environment variables only — set them as Railway service variables. `.env` and `config.json` stay gitignored.
6. **Operate from the project root.** Use relative paths; avoid `cd`.

---

## Quality Standards

| Metric | Threshold | Tool |
|--------|-----------|------|
| Code coverage | ≥90% (branch) | pytest-cov |
| Cyclomatic complexity | ≤10 per function | ruff (mccabe) / xenon |
| Type checking | strict, clean | mypy |
| Lint | clean (ruff `ALL` ruleset) | ruff |
| Formatting | enforced | ruff format |
| Security | no findings | bandit, pip-audit |
| Dead code | none | vulture |

All thresholds are defined once in `pyproject.toml` and enforced by **`pre-commit run --all-files`** — the single local quality gate — and re-run identically in CI (`.github/workflows/ci.yml`). Mutation testing (`mutmut`) is a periodic gate, not run continuously.

Tests follow the AAA pattern and TDD (see the `testing` and `mutation-testing` skills). Every text-lookup command and the central interaction handler should have unit coverage.

---

## Project Overview

**Poimandres** is a Discord bot that quotes esoteric, occult, religious, and philosophical texts on demand via **slash commands**. A user types e.g. `/ch 1.2` and the bot replies with the requested passage inside a Discord embed. The bot is themed around Hermeticism; its name comes from the *Corpus Hermeticum*.

The bot has **no database**. All content lives in static JSON files; every command is a thin lookup: take the user's input string, use it as a key into a JSON object, return the matched value (or a "Not found" message).

**16 slash commands**: `ch, ah, dh, oh, emeraldtablet, bible, quran, sepher-yetzirah, al, enchiridion, aurelius, proclus-metaphysics, yoga, tarot, help, contents`.

---

## Architecture (Python target)

Target layout — see spec section 4 for detail:

```
poimandres/
├── bot.py                 # main entry point (replaces index.js)
├── deploy_commands.py     # slash-command sync (replaces deploy-commands.js)
├── server_count.py        # standalone guild-count utility
├── commands/              # one module per command
├── books/                 # verbatim JSON data files (from commands/books/)
├── railway.json
├── requirements.txt
└── README.md
```

**Tech stack**: Python 3.10+, `discord.py` 2.x (slash commands via `discord.app_commands`), Railway-injected environment variables for config, `pytest` for tests.

**Shared conventions** (spec section 5): embeds use color `#f15b40`; footers are built from each book JSON's `bookTitle` / `translator` metadata keys; `:` is normalized to `.` in lookup keys for most commands; `/help` and `/contents` reply ephemerally, all other replies are public; a global error guard turns any exception into an ephemeral error message plus a console log.

---

## Development Workflow

```bash
# 0. One-time setup: install the toolchain and git hooks
pip install -r requirements-dev.txt
pre-commit install && pre-commit install --hook-type commit-msg

# 1. Branch off the migration branch
git checkout claude/well-worn-tools-migration-H17cH

# 2. Write a failing test, then the code to pass it
#    (Red → Green → Refactor)

# 3. Run the single quality gate before committing
pre-commit run --all-files

# 4. Commit only when green (conventional-commit message, enforced by commitizen)
git commit -m "feat(commands): add /ch lookup command"

# 5. Push to the designated branch
git push -u origin claude/well-worn-tools-migration-H17cH
```

**Branch**: all work goes to `claude/well-worn-tools-migration-H17cH`. Do not push to `main` without explicit permission.

---

## Common Mistakes

1. **Editing the corpus JSON.** The passage text is hand-curated public-domain scripture — copy it byte-for-byte, never alter it.
2. **Committing secrets.** Token and IDs belong in Railway service variables, never in tracked files.
3. **Adding features beyond the spec.** Functional parity with the Node.js bot is the goal; the spec lists the few intentional deviations that are allowed.
4. **Lowering quality thresholds** instead of writing more tests or refactoring.
5. **Bypassing checks** with `# noqa` / `# type: ignore` instead of fixing the root cause.

---

## Appendix: Key Files

- `plans/python-recreation-prompt.md` — the build spec (authoritative)
- `CLAUDE.md` — this file
- `pyproject.toml` — single source of truth for dependencies and every tool config
- `.pre-commit-config.yaml` — the local quality gate (lint, type, security, tests)
- `.github/workflows/ci.yml` — CI: pre-commit gate, test matrix (3.10–3.12), dependency audit
- `requirements.txt` — runtime dependencies (mirrors `pyproject.toml`)
- `requirements-dev.txt` — dev/CI install: editable package + dev toolchain + security constraints
- `constraints.txt` — transitive-dependency security pins (CVE remediation)
- `railway.json` — Railway build/deploy config (Nixpacks builder, bot start command)
- `.claude/skills/` — well-worn-tools skill collection
- `poimandres/` — the Python package (target of the migration)
- `commands/books/*.json` — the verbatim text corpora to carry over
- `index.js` / `commands/` — original Node.js implementation (reference only)
- `README.md` — project overview and the Hermetic epigraph

## Appendix: Intentional Deviations

When the Python bot deviates from the Node.js original, record it here and in the PR description. Candidates noted in the spec:

- The original `/help` omits `/yoga`; adding a `/yoga` field is a reasonable fix.
- The original `/tarot` does no bounds checking; adding it is optional.
- The spec specifies `python-dotenv` for config; the bot now deploys on Railway
  and reads configuration straight from the process environment. `python-dotenv`
  and `.env.example` were removed; `railway.json` defines the deployment.
