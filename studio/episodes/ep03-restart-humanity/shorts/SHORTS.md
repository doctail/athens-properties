# EP03 Shorts - specs ready, voiceover NOT generated

Status: specs validated (JSON parses, all images exist, 12 shots each). Not rendered: the mp3 files do not exist yet and the voice (vsub text_to_speech, voice "Bill") needs the owner's explicit OK.
Render later: `python3 studio/tools/render_short.py studio/episodes/ep03-restart-humanity/shorts/<spec>.json`
Renderer rules: one narration line = one phrase; the audio must have a clear pause between phrases (5 phrases per Short; the renderer matches speech chunks by silence detection and asserts the count). Generate the 5 lines as 5 separate takes, or with a clear pause, and check the chunk count. `seamless: true` = no boom at t=0. Hook and badge are static from frame 1. Crop format: [image, zoom, cx, cy].
Known limit: each shot zooms 6% during its hold, so the last frame ends slightly tighter than the first frame; the cut back to the start hides it. V10, V29 are not used. V25 unused.
All claims come from sources.md (#1 rule of thumb ~50 for wild animals, #3 inbreeding depression, #5 bands of dozens, #6 first child not inbred). Wording is hedged.

## S1 - s1-two-people.json (Wed 2026-11-18), survival reveal loop, V01-V09
Hook: TWO PEOPLE. ONE WINTER. | Badge: COULD THEY LAST?
Narration (24 words, loop: last line runs into the first):
1. Two people, one beach.
2. No shelter, no food.
3. Then the first winter hits.
4. One bad week could end it.
5. And winter doesn't care about... (loops into "Two people, one beach.")
Shots (12, ~0.7 s each): 1 V01 full | V02 full; 2 V02 medium on camp (z2.2) | V03 full | V03 detail on hands (z1.9); 3 V04 full | V09 full; 4 V05 | V06 | V07; 5 V08 | V01 full (= first frame, V10 never used).
Title: Two people. One bad winter. 🥶 #shorts
Description: Could two people restart humanity? Not without a lot of luck. #whatif #survival #shorts

## S2 - s2-fifty.json (Thu 2026-11-19), size shock, V11-V19 (V12 first/last)
Hook: HOW MANY TO RESTART? | Badge: NEED ~50. HAVE 2.
Narration (22 words, loop):
1. Two people.
2. Rule of thumb for wild animals:
3. about fifty, to avoid rapid inbreeding.
4. Hunter-gatherer bands were usually dozens.
5. Dave's group? Just... (loops into "Two people.")
Shots (12): 1 V12 wide | V12 detail on the two (z2.2); 2 V19 | V15; 3 V13 wide | V13 medium (z2.0) | V11; 4 V17 wide | V17 medium (z1.9) | V16; 5 V14 (crowd vs Dave) | V12 wide (= first frame).
Title: You need about 50 people. Dave has 1 friend. 😬 #shorts
Description: Conservation biologists use ~50 as a rule of thumb to avoid rapid inbreeding. Two people are nowhere near. #whatif #history #shorts

## S3 - s3-myth.json (Sat 2026-11-21), myth bust, V21-V28, V30 (V29 red cross NOT used)
Hook: RESTART HUMANITY? | Badge: MYTH
Narration (25 words, loop):
1. Myth: two people can restart humanity.
2. Their first child? Probably fine.
3. Then grandchildren would pair with relatives.
4. More miscarriages, weaker immune systems.
5. Don't believe the... (loops into "Myth: ...")
Shots (12): 1 V21 full | V21 face detail (z1.9) | V30 full (mid-Short only, not closing); 2 V28 full | V28 face (z2.0); 3 V22 full | V22 detail on the X (z2.2); 4 V23 | V24 | V26; 5 V27 | V21 full (= first frame, loop closes on V21 not V30).
Title: Myth: any 2 people can restart humanity ❌ #shorts
Description: Genetics, workload and bad luck say otherwise. #whatif #survival #shorts
