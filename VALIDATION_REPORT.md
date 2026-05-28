# Validation report — antrop-personas v0.11.0-rc1

Date: 2026-05-27 (structural pass); carried forward to v0.11.0-rc1
Run by: Cowork session validation pass

> **Note (0.11.0-rc1):** This report was first written at rc2 and has been carried
> forward. The plugin now ships **10 skills** (added `polish-language`) and
> **6 agents** (added `language-polisher`). The structural checks below still
> hold; the end-to-end run was executed on 2026-05-28 (see `HANDOFF_TO_NEW_CHAT.md`).
> Counts in the table reflect the current 0.11.0-rc1 component set.

## Status

**Release candidate.** All structural checks pass. End-to-end test against real interview material is still pending — to be run in a fresh chat following `HANDOFF_TO_NEW_CHAT.md`.

### Changes since rc1

- `start-persona-project` now asks three setup questions before scaffolding: output language, persona methodology, brand profile. Answers are written into `state.json` and `.persona-config.md`. The command's conversation then matches the chosen language.
- Cross-cutting principles updated: language is now explicit-flexible (`sv` default, `en`, `bilingual`, or any other code), with a hard no-drift rule once set.
- HANDOFF supports two test modes: **Mode A** (no comparison baseline) and **Mode B** (compare against human-made personas from an old project — much stronger validation than AI-vs-AI). The AI-generated NV v1 baseline is explicitly ignored.

## What was tested

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Skill frontmatter (`quick_validate.py`) | PASS (10/10) | All skills validate cleanly. Earlier issue (`version:` at top level) fixed by moving to `metadata.version`. |
| 2 | Description length | PASS (10/10) | All descriptions within the 1023-char limit. |
| 3 | Plugin manifest (`.claude-plugin/plugin.json`) | PASS | Valid JSON. Declares dependencies, components, docs. |
| 4 | Marketplace manifest (`.claude-plugin/marketplace.json`) | PASS | Earlier failure `plugins.0.source: Invalid input` fixed — `source` is now an object `{ source: "local", path: "." }`. |
| 5 | Pipeline-state contract | PASS (10/10) | Every SKILL.md has a `## Pipeline state` section declaring required-before and config-override behaviour. |
| 6 | Five-beat checkpoint flow | PASS (10/10) | Every SKILL.md has Read / Propose / Checkpoint / Produce / Falsify as numbered subheadings. |
| 7 | Hand-off integrity | PASS | Each skill's input paths match the previous skill's output paths. No broken hand-offs. |
| 8 | Agent files exist | PASS (6/6) | interview-reader (haiku), thematic-analyser (opus), archetype-drafter (opus), audit-runner (opus), card-renderer (sonnet), language-polisher (sonnet) all present. |
| 9 | Agent delegation references | PASS | Every `${CLAUDE_PLUGIN_ROOT}/agents/<name>.md` referenced from a SKILL.md exists. |
| 10 | Trigger coverage (audit) | PASS | 11 missing triggers added after structural audit; full natural-phrase coverage in both Swedish and English. |
| 11 | Token-efficient working format | PASS | `clean-interview` now explicitly converts `.docx` input to `.md`; cross-cutting principles document the policy. |
| 12 | Scalability guidance (30+ interviews) | PASS | Batch-and-merge pattern added to `analyse-themes` and `frame-and-cluster`. |
| 13 | Dependencies declaration | PASS | `docx` declared required; `gemini-image-gen` + `canvas-design` recommended. Graceful-fail messages documented in `DEPENDENCIES.md`. |
| 14 | Per-project configuration | PASS | `settings/local.md.example` documents language, anonymisation policy, methodology defaults, brand-overrides, delegation knobs, file-format. |
| 15 | **End-to-end run on Naturvårdsverket material** | **PENDING** | Source files in `Downloads/Odevo workshop docs/` not accessible from this sandbox. To run, install this `.plugin` in a fresh Cowork session with the folder mounted. See `HANDOFF_TO_NEW_CHAT.md`. |

## What changed in this validation pass

Compared to v0.1.0:

### Added

- `agents/` directory with 5 sub-agents (haiku × 1, sonnet × 2, opus × 2)
- `settings/local.md.example` — project-local configuration overrides
- `references/pipeline-state.md` — state-file contract and graceful-fail behaviour
- `DEPENDENCIES.md` — hard/soft skill dependencies with graceful-fail messages
- `HANDOFF_TO_NEW_CHAT.md` — prompt for running the E2E test in a fresh session
- Per-skill `## Pipeline state` section declaring required-before
- Working-format policy: `.md` everywhere except client deliveries; `.docx` input gets converted at `clean-interview`
- Scalability guidance for 30+ interviews in `analyse-themes` and `frame-and-cluster`
- Delegation blocks in 5 SKILL.md files referencing the new agents
- 11 additional trigger phrases (mix of SV and EN) across the descriptions

### Fixed

- `marketplace.json` `plugins.0.source` shape (object, not string) — passes `claude plugin validate marketplace.json`
- All SKILL.md frontmatter — moved invalid top-level `version:` into `metadata.version`
- `plugin.json` enriched with explicit dependencies block and component counts

### Bumped

- `0.1.0` → `0.9.0-rc2`. **Do not bump to 1.0.0** until the E2E test passes.

## What is still open

1. **End-to-end test against real NV transcripts.** Required for v1.0.0. Procedure documented in `HANDOFF_TO_NEW_CHAT.md`. Compare outputs to the existing `Validity Audit — Behavioural Archetypes.docx` and `NV personas.pdf` for regression detection.
2. **Trigger fire-rate test.** The expanded descriptions cover the audit's MISSes but the real-world fire rate (does "kan du köra en analys" actually trigger `analyse-themes` reliably?) needs a behavioural test, not a substring check. Run in a fresh session with the plugin installed.
3. **Per-agent model overrides via `.persona-config.md`.** Documented in the settings file but not yet wired through to actual agent invocation. If the analyst sets `audit-runner-model: sonnet`, the plugin currently still uses the opus declared in the agent's frontmatter. Wiring this is a v1.1 item.

## Recommendation

Ship v0.11.0-rc1 as the testable artefact. Bump to v1.0.0 only after step 1 above completes cleanly (no regressions vs. the NV v1 reference deliverables).
