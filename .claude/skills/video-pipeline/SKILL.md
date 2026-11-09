---
name: video-pipeline
description: Runs the faceless YouTube production team end to end (niche → channels → outliers → formula → production → analysis → optimization). Use when the owner says "run the pipeline", "next episode", "weekly review", or names one stage.
---

# Video pipeline orchestrator

Read `studio/CHANNEL.md` and `studio/credits.md` before anything else. Report the vidIQ credit balance (`vidiq_balance`, free) at the start.

## Stages and agents
| # | Stage | Agent | Output |
|---|---|---|---|
| 1 | Niche & keywords | `niche-scout` | studio/research/keywords-*.md |
| 2 | Top channels | `channel-analyst` | studio/research/channels.md |
| 3 | Top & outlier videos | `video-analyst` | studio/research/outliers-*.md |
| 4 | Reverse engineering | `reverse-engineer` | studio/research/formula.md |
| 5 | Production | `producer` | studio/episodes/<slug>/ |
| 6 | Performance analysis | `performance-analyst` | studio/reports/*.md |
| 7 | Corrections & republishing | `optimizer` | live changes + formula changelog |

## Modes
- **Setup** (once): 1 → 2 → 3 → 4, then create `studio/style.md` (character + visual style) and get owner approval.
- **Next episode**: pick the top unused topic from the latest keywords file → 5. Gates: script approval, preview approval, publish approval.
- **Review**: 6 at 48h / 7d / 28d after each upload and weekly for the channel → 7.
- **Refresh research**: every 2–4 weeks, 1 and 3 only (research goes stale fast in this niche).

## Rules
- Stages 2 and 3 are independent: run them in parallel.
- Skip a stage whose output file is fresher than 14 days unless the owner asks.
- Budget: if the credit balance cannot cover a stage, say so and propose what to do with free tools only; do not start a stage you cannot finish.
- Human gates are mandatory: nothing goes public or changes on a live video without the owner's explicit OK.
