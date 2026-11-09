# EP01 status

- [x] Script v1 approved by owner (2026-11-09): #1 Miocene OK, Dave speaks via speech bubbles only, survival times disclosed as estimates.
- [x] Narrator voice: vsub/ElevenLabs "Bill" (pqHfZKP75CvOlQylNhV4), speed 100, stability 55, similarity 75, style 15.
- [x] Test narration scene #5 Carboniferous: audio/scene05-carboniferous.mp3 (69.0 s, 853 chars).
- [ ] Test animation scene #5 — BLOCKED: needs full-resolution images.
- [ ] Full narration
- [ ] Full animation
- [ ] Titles / thumbnail / description (manual upload by owner)

## Production route (decided 2026-11-09)
- vsub code video (Remotion hosted) → not available on the account ("Code videos are not available yet").
- vsub create_ai_video_v3 → works, but draws its own generic characters: Dave would not be consistent. Fallback only.
- **Chosen: local render** in this container (ffmpeg 6.1 present, Remotion installable from npm): Gemini images of Dave at full res + vsub voiceover + our own timer/tier-board/caption overlays.
- ~~Blocker: Gemini API key rejected (API_KEY_INVALID).~~ Resolved 2026-11-09: key is now accepted.
- **Current blocker (2026-11-09):** the key's Google project is on the Free Tier, where `gemini-3.1-flash-image` has a quota of **0** (429 RESOURCE_EXHAUSTED, `limit: 0` on requests/day, requests/min and input tokens/min). Waiting does not fix it. Fix: enable billing on that project in AI Studio (Tier 1), or switch `GEMINI_MODEL` to an image model that has free-tier quota on this account. Test call that failed: scene #5 keyframe (edit_image from the Dave model sheet, 16:9).
