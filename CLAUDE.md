# CLAUDE.md — working on the antrop-personas plugin

This repo is the **source of a Claude Code / Cowork plugin**, not an app. The
deliverable is a set of skills, agents, and a command that another Claude runs.
Edit the markdown contracts; there is almost no executable code (two small Python
helpers only).

## Layout

- `skills/<name>/SKILL.md` — 11 skills. 8 main-path steps (clean-interview →
  analyse-themes → frame-and-cluster → generate-archetypes → validate-archetypes
  → design-archetypes → polish-language → package-for-client), 2 side-branches
  (interview-cards, compare-baseline), 1 orchestrator (run-pipeline).
- `agents/<name>.md` — 6 sub-agents the skills delegate to.
- `commands/start-persona-project.md` — the scaffolding entry point.
- `references/` — the **authoritative shared contracts**. Read these first:
  - `cross-cutting-principles.md` — the five principles + the checkpoint mechanic
    + the `mode: auto` / `dry-run` / `skip-checkpoints` contract.
  - `pipeline-state.md` — `state.json` schema, required-before contract, auto-mode
    state fields.
  - `pitfalls-from-nv-v1.md` — concrete failures baked in as warnings.
- `settings/local.md.example` — every per-project config knob.

## House style (match it; don't invent a new shape)

- SKILL.md frontmatter: `name` (== dir name), a quoted `description`, and a
  `metadata:` block with `version`, `pipeline-step`, `works-on`, and an explicit
  `triggers:` YAML list (Swedish **and** English natural phrases). **Never** put
  `version:` at the top level — it must live under `metadata`.
- Every step-skill body has a `## Pipeline state` section and the five numbered
  beats: Read → Propose → Checkpoint → Produce → Falsify.
- Agent frontmatter: `name`, `description`, `model`, `effort`, `tools`.
- Reference other plugin files as `${CLAUDE_PLUGIN_ROOT}/path`.
- Keep comments/prose tight; this is a fast-moving internal tool.

## The three execution modes (don't conflate them)

| `.persona-config.md` `process` | Meaning | Quality |
|---|---|---|
| `mode: interactive` (default) | Analyst approves every checkpoint | Full |
| `mode: auto` | Unattended run; applies + logs documented defaults | **Full** |
| `dry-run: yes` | Preview / prompt-debugging | Reduced |
| `skip-checkpoints: yes` | Synthetic / test data | Reduced, stamped synthetic |

`mode: auto` is the load-bearing new capability: it bypasses the three strict
checkpoints (B2/I1/D0) **deliberately**, logs decisions to
`09-auto/auto-decisions.md`, never reduces quality, and stamps a review banner on
open CRITICAL findings instead of halting. If you change checkpoint behaviour in
any skill, keep the auto-mode branch consistent with
`references/cross-cutting-principles.md` § "`mode` (autonomous run)" — that file
is the single source of truth.

## Model IDs are real — do not "correct" them

`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001` are current,
valid identifiers. Don't downgrade them to older names that look more familiar.

## When you change something

- Keep counts in sync across `plugin.json` (`metadata.components`),
  `marketplace.json`, `README.md`, and `VALIDATION_REPORT.md`.
- Bump the version in `plugin.json` **and** `marketplace.json` (3 places) **and**
  the README footer, and add a `CHANGELOG.md` entry. Bump only "this IS version
  X" statements; leave "introduced in rcN" history alone.
- Validate before packing:
  ```
  python3 -m py_compile skills/*/references/*.py
  python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('.claude-plugin/*.json')]"
  ```
- Pack as an uncompressed zip from **inside** this directory:
  `zip -r -0 ../antrop-personas-<version>.plugin . -x '.git/*' '*/__pycache__/*'`

## Never commit

Client interview data, `__pycache__/`, `*.pyc`, `.DS_Store`, `node_modules/`,
or packed `*.plugin` artefacts (all in `.gitignore`). This plugin encodes
methodology from real client engagements — the client material itself stays out.
