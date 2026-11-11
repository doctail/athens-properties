---
name: video-pipeline
description: Runs the 4-channel faceless YouTube studio (Dave vs History, Year Built, Focus Flow Lab, TreasureXpert) — research, production, analysis, optimization — with memory in Nodum. Use when the owner says "run the pipeline", "next episode", "weekly review", names a channel, or names one stage.
---

# Video pipeline orchestrator (4 channels)

Run on Sonnet by default; switch to Opus only for strategy (new format, niche change, monthly review).

## Start of every run (cheap, in this order)
1. `vidiq_balance` (free) and say the balance.
2. Nodum vault "My Vault": read `00 HQ/RULES`, `00 HQ/CALENDAR`, `00 HQ/LEDGER` (quota section only).
3. Pick ONE channel (from the owner's words or the CALENDAR). Read only `CH <Channel>/CARD <Channel>` and `STATUS <Channel>` (Focus/Treasure: `BACKLOG <Channel>`).
Never load two channels' folders in the same step. For a multi-channel review, run the channels one after another and keep only each channel's 5-line summary.

## Channels
| Key | Nodum folder | Production files | Recipe |
|---|---|---|---|
| dave | `CH Dave` | repo `studio/episodes/<slug>/` | stages below |
| yearbuilt | `CH Year Built` | repo `doctail/city3d` | `PRODUZIONE_TIMELAPSE.md` in city3d (Blender on a RunPod pod, owner's OK every time) |
| focus | `CH Focus` | repo `studio/focus/<slug>/` | `RECIPE Focus` (ffmpeg, 0 credits) |
| treasure | `CH Treasure` | repo `studio/treasure/<slug>/` | `RECIPE Treasure` |

## Stages and agents (model in brackets, see `00 HQ/MODELS`)
| # | Stage | Agent | Output (Nodum unless stated) |
|---|---|---|---|
| 1 | Niche & keywords | `niche-scout` [sonnet] | CH <Channel>/research/keywords-<date> |
| 2 | Top channels | `channel-analyst` [haiku] | CH <Channel>/research/channels |
| 3 | Top & outlier videos | `video-analyst` [haiku] | CH <Channel>/research/outliers-<date> |
| 4 | Reverse engineering | `reverse-engineer` [sonnet] | FORMULA note of the channel |
| 5 | Production | `producer` [sonnet] | repo files + STATUS note |
| 6 | Performance analysis | `performance-analyst` [haiku] | CH <Channel>/reports/<date> |
| 7 | Corrections & republishing | `optimizer` [haiku] | live changes (owner OK) + STATUS log |

Always pass the channel key in the agent prompt, plus the single input note it needs. Agents never call each other: they hand off through STATUS notes.

## Modes
- **Next episode** (per channel): top unused row of BACKLOG / FORMULA → 5. Gates: script approval (Dave, Treasure), preview approval, publish approval.
- **Weekly review** (Monday, one session): for each channel in turn → 6 → 7; one report per channel; update CALENDAR.
- **Refresh research**: every 2–4 weeks per channel, 1 and 3 only. Skip any stage whose output note is fresher than 14 days.
- Focus needs no research or LLM beyond metadata; Year Built needs only `youtube_search` on the next city (before the render and before publishing).

## Rules
- Stages 2 and 3 are independent: run them in parallel.
- Budget: follow the quotas in `00 HQ/LEDGER`. If the balance cannot cover a stage, say so and propose free alternatives; do not start a stage you cannot finish.
- Human gates are mandatory: nothing goes public, no live video changes, no pod and no paid generation without the owner's explicit OK.
- Focus and Treasure are not connected to vidIQ (see `00 HQ/ACCOUNTS`): their private analytics come from the owner (YouTube Studio numbers pasted in chat).
