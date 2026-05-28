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
  `metadata:` block. **The `metadata:` block must be a flat string → string map** —
  the agentskills.io validator (which Cowork enforces, stricter than the local CLI)
  rejects non-string values. So:
  - `version` and `pipeline-step` are **quoted strings** (`"1.1.0"`, `"2"`), not
    bare integers.
  - `side-branch` is `"true"` (a string), not a bool.
  - `triggers` is **one comma-separated string** (Swedish **and** English natural
    phrases), **not** a YAML list. Wrap any literal `"` inside a phrase as `'`.
  - **Never** put `version:` at the top level — it must live under `metadata`.
  - Top-level keys stay limited to `name`, `description`, `metadata`. (`description`
    + any `when_to_use` is truncated at ~1,536 chars in the listing — that is what
    actually drives invocation; `metadata.triggers` is documentation only.)
- Every step-skill body has a `## Pipeline state` section and the five numbered
  beats: Read → Propose → Checkpoint → Produce → Falsify.
- Agent frontmatter: `name`, `description`, `model`, `tools`. (No `effort:` field —
  it is not in the schema; effort intent is documented in `DEPENDENCIES.md`.)
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

## Model selection in agents — use tier aliases

Agent frontmatter uses the portable tier aliases `model: opus` / `sonnet` / `haiku`,
which resolve to the current top model per tier on whatever host runs the plugin.
Prefer these over pinned IDs so the plugin doesn't rot when a new model ships.

The full IDs `claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`
are current and valid if you ever need to pin — don't "downgrade" them to older
names that look more familiar.

## When you change something

- Keep counts in sync across `README.md` and `VALIDATION_REPORT.md`. (`plugin.json`
  no longer carries a `metadata.components` block — it was non-standard and was
  removed; component counts live in the docs only.)
- Bump the version in `plugin.json` **and** `marketplace.json` **and** the README
  footer, and add a `CHANGELOG.md` entry. Bump only "this IS version X" statements;
  leave "introduced in rcN" history alone.
- Validate before packing:
  ```
  python3 -m py_compile skills/*/references/*.py
  python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('.claude-plugin/*.json')]"
  # assert every SKILL.md metadata value is a string (the rule Cowork enforces):
  python3 -c "import glob,yaml; [[print('NON-STRING',p,k) for k,v in (yaml.safe_load(open(p).read().split('---')[1]).get('metadata') or {}).items() if not isinstance(v,str)] for p in glob.glob('skills/*/SKILL.md')]"
  ```
- Pack as an uncompressed zip from **inside** this directory, **excluding
  `marketplace.json`** (a direct `.plugin` install only needs `plugin.json`; the
  marketplace manifest stays in the repo for the local-marketplace path):
  `zip -r -0 ../antrop-personas-<version>.plugin . -x '.git/*' '*/__pycache__/*' '.claude-plugin/marketplace.json'`

## Never commit

Client interview data, `__pycache__/`, `*.pyc`, `.DS_Store`, `node_modules/`,
or packed `*.plugin` artefacts (all in `.gitignore`). This plugin encodes
methodology from real client engagements — the client material itself stays out.
