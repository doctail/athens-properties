# EP05 Shorts — texts (not voiced, not rendered)

Status: DRAFT v1 (2026-11-20). Voice and render come after the owner's OK (vsub "Bill", stability 55, similarity 75, style 15, speed 100; about 30 words per Short, roughly 50 credits in total, not spent). Images: V01–V33 from flow-prompts.md runs 6 to 8.
Rules as EP03/EP04: 5 phrases per Short (5 separate takes, joined with 0.7 s pauses and sped up 1.12x so silence detection finds exactly 5 chunks), 11 to 12 shots (~0.7 s), static hook + badge from frame 1, no opening boom (`seamless`), last phrase runs into the first. Loop frames: the LAST shot is the hook image (V01 / V12 / V23) at the same crop as the first shot. V11, V22, V33 are prompted with the same framing as the hook frames, but use the first-image crop if they do not match (EP04 lesson). Hook frames keep the top 20% calm for the static text.
Spec JSON files (s1-..., s2-..., s3-...) are written after the voice with `render_short.py` conventions (see EP04 shorts/*.json). Run: `python3 studio/tools/render_short.py studio/episodes/ep05-ice-age/shorts/<spec>.json`.
Every line states a hedge where the source is an estimate or an inference (sources.md).

## S1 — myth bust (images V01–V11)
Hook: FROZEN EVERYWHERE? NO. | Badge: MYTH
Narration (about 28 words):
1. Frozen everywhere? No.
2. Ice covered about a quarter of the land.
3. Most of Asia? No ice sheets.
4. Dave's Europe: cold, dry grassland.
5. So was the Ice Age really (loops into "Frozen everywhere? No.")
Shots: p1 V01, V02 | p2 V04, V05 | p3 V06, V10 | p4 V03, V09, V07 | p5 V08, V01 (= first frame).
Sources: #1 (Clark 2009: LGM about 26.5 to 19 ka), #3 (about a quarter of land vs about 11% today), #6 (Asia and Africa without ice sheets; cold, dry grassland in Eastern Europe).
Title: Was the Ice Age frozen everywhere? No. #shorts
Description: Ice sheets covered about a quarter of the world's land at the Last Glacial Maximum, against around 11% today. Most of Asia and Africa had no ice sheets at all (Clark et al., 2009; USGS). #history #iceage #shorts

## S2 — curiosity fact (images V12–V22)
Hook: NO TREES? BURN BONES. | Badge: ICE AGE FUEL
Narration (about 29 words):
1. No trees? Burn bones.
2. At Mezhyrich, hearths held burned bone.
3. Almost no wood charcoal.
4. Researchers read it as fuel.
5. So where's Dave's firewood? (loops into "No trees? Burn bones.")
Shots: p1 V12, V13 | p2 V14, V15, V16 | p3 V16, V18 | p4 V19, V20, V17 | p5 V21, V12 (= first frame).
Sources: #12 (Mezhyrich burned bone; deliberate fuel still being tested, so the caption says "read it as"), #13 (Lascaux lamp, shown in V19–V20 only as a visual of fat-and-wick light; not narrated).
Title: No trees? Ice Age hunters may have burned bones. #shorts
Description: At Mezhyrich in Ukraine, hearths held lots of burned bone and almost no wood charcoal. Researchers read this as bone burned for fuel where wood was scarce; whether it was deliberate is still being tested. #history #iceage #shorts

## S3 — size shock (images V23–V33)
Hook: ONE MAMMOTH: 3.5 MILLION CALORIES? | Badge: BY ONE ESTIMATE
Narration (about 30 words):
1. Mammoth: millions of calories?
2. By one estimate, three and a half million.
3. Muscle alone.
4. A big male: eleven feet tall.
5. So how big is one (loops into "Mammoth: millions of calories?")
Shots: p1 V23, V24 | p2 V26, V25 | p3 V28, V27 | p4 V25, V31, V29 | p5 V30, V23 (= first frame).
Sources: #16 (Cole 2017, about 3.6 million calories of muscle, press summary), #20 (about 11 ft at the shoulder, up to about 8 tons; Wikipedia / Siegsdorf specimen). Say "about", "by one estimate", never "exactly".
Title: One mammoth, about 3.5 million calories? #shorts
Description: By one estimate (Cole, 2017), the muscle of a single mammoth held about 3.6 million calories. A big male stood about 11 feet at the shoulder. #history #iceage #mammoth #shorts
