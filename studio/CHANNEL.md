# Channel brief — single source of truth for every agent

## Channel
- YouTube channel ID: `UCn6MaFlCc_8zsyzCG1Ly62g` (formerly "TextHook" — old Shorts set to private, rebrand pending)
- New name / handle: TBD (Niche Scout proposes, owner decides)
- Language: English. Target markets for titles/topics: US, UK, CA, AU (higher RPM than the PK/IN/VN/BD search base).

## Niche (validated 2026-11-09 with vidIQ)
Animated explainers on **how humans survived in the past**: prehistoric eras, ancient civilizations, "what if" survival scenarios.
Formats that win: "How long would you survive in every era?", "How did ancient humans [everyday problem]?", "Life 20,000 years ago", "Could 2 people restart humanity?".

Evidence (month-over-month, vidIQ rising keywords):
- "how long would you survive in every era of earth?" +6864%, ~131k searches/mo, competition 38
- "how did ancient humans get any privacy?" +1855%, ~113k/mo
- "can 2 people really restart humanity?" +333%, ~387k/mo
- Format channels searched by name: Depth Theory (3.06M, +635%), Archive in Minutes (788k, +655%), StickOrbit (509k, +473%), Squire Explains (668k, +284%)
- Breakout channels: Through the Ages (3.7k subs → 690k / 583k / 168k views), Primordia (15.7k subs → 358k)

## Known risks
1. Low RPM: search demand skews PK/IN/VN/BD. Angle topics/titles at US/UK viewers.
2. Copycats: several <300-sub channels already clone the same titles. Differentiate with a **recurring named character** and a consistent visual style.
3. Low engagement (0.1–0.5%) in the niche: build a series/character so viewers have a reason to subscribe.
4. YouTube "inauthentic / mass-produced content" policy: every script must be original, fact-checked, with sources; no fabricated "true stories"; disclose AI-altered realistic content when required.

## Production stack (all available to Claude in this project)
- Research/analytics/upload: vidIQ MCP (`mcp__vidIQ_for_Claude__*`)
- Images: **Google Flow, run by the owner** from multi-prompt files Claude writes (`studio/episodes/<slug>/flow-prompts.md`: one HEADER + numbered prompts per run, Dave model sheet attached as reference). Owner drops the images in `images/`. No API image generation (nanobanana/Gemini dropped 2026-11-10: no paid billing).
- Animation: vsub code video (Remotion) `mcp__vsub__code_video_*`; alternative `create_ai_video_v3`
- Voiceover / music: vsub `text_to_speech`, vidIQ `vidiq_voiceover_generate`, `vidiq_generate_music`
- Titles / thumbnails / scoring: vidIQ `generate_titles`, `generate_thumbnail`, `score_title`, `score_thumbnail`

## Hard rules
- **Credit budget**: vidIQ credits are scarce. Before any paid call, state its cost and log it in `studio/credits.md`. Prefer free tools (0-credit) and reuse saved research in `studio/research/`.
- **Human gate**: nothing is published, made public, or changed on a live video without the owner's explicit "OK" in chat.
- Every agent writes its output to a file under `studio/` so the next agent reads it instead of re-researching.
