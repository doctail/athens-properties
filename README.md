# Athens Properties — YouTube studio (4 channels)

Code and production files for Dave vs History, Focus Flow Lab and TreasureXpert. Year Built lives in `doctail/city3d`.

**Knowledge lives in Nodum** (vault "My Vault"): start from `00 HQ/00 START`. Brief, formula, research, status, calendar and the credit ledger are there and nowhere else. This repo holds only:
- `.claude/agents/` — 7 agents, each with its model (see Nodum `00 HQ/MODELS`) and a channel-scoped load protocol.
- `.claude/skills/video-pipeline/` — the orchestrator.
- `studio/episodes/<slug>/` — Dave production files (script, flow-prompts, edit.json, images, audio, metadata). The renderer reads them from here.
- `studio/focus/<slug>/`, `studio/treasure/<slug>/` — production files of the other two channels.
- `studio/tools/` — renderers (`render_episode.py`, `render_short.py`, `mix_music.sh`, `make_sfx.py`) and `focus/` (`noise.sh`, `thumb.py`).
- `studio/assets/` — Dave brand assets.

## MCP servers (`.mcp.json`)
- **nodum** — the token is a network secret on the cloud environment; the header in `.mcp.json` is only a placeholder.
