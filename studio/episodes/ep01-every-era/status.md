# EP01 status

- [x] Script v1 approved by owner (2026-11-09): #1 Miocene OK, Dave speaks via speech bubbles only, survival times disclosed as estimates.
- [x] Narrator voice: vsub/ElevenLabs "Bill" (pqHfZKP75CvOlQylNhV4), speed 100, stability 55, similarity 75, style 15.
- [x] Test narration scene #5 Carboniferous: audio/scene05-carboniferous.mp3 (69.0 s, 853 chars).
- [ ] Test animation scene #5:
  - Canva images (consistent Dave, good quality): shots MAHaa20ATek (establishing), MAHaa8G8fCE (deep breath). Canva FREE plan = 20 AI images/month, quota exhausted on 2026-11-09, resets 2026-12-01 00:00 UTC. Not enough for ~60-100 images/episode.
  - vsub v3 test (style Cartoon 1, voice Bill), project 912797e1-acd9-4a91-97b7-349b4c45046d, editor https://vsub.io/workspace/editor?id=912797e1-acd9-4a91-97b7-349b4c45046d — processing (up to 3 h). Check: is Dave consistent across shots?
- [ ] Full narration
- [ ] Full animation
- [ ] Titles / thumbnail / description (manual upload by owner)

## Production route (decided 2026-11-09)
- vsub code video (Remotion hosted) → not available on the account ("Code videos are not available yet").
- vsub create_ai_video_v3 → works, but draws its own generic characters: Dave would not be consistent. Fallback only.
- **Chosen: local render** in this container (ffmpeg 6.1 present, Remotion installable from npm): Gemini images of Dave at full res + vsub voiceover + our own timer/tier-board/caption overlays.
- Owner decision 2026-11-09: no paid Gemini billing. Bill voice approved.
- Former blocker: Gemini API key rejected (API_KEY_INVALID). Owner must add a valid key as a network secret (host generativelanguage.googleapis.com, header x-goog-api-key) in the cloud environment "athens-properties".
