# EP05 — upload metadata (FINAL, render done, NOT uploaded)

Status: v2 (2026-11-20). Render `build/final_music.mp4` = 7:15.8 (435.8 s), QA render PASS (-15.1 LUFS, true peak -2.4 dBTP). Chapters below are computed from the real section timings of that render (cold open starts at 0:00). Recompute only if the video is re-rendered. Upload is manual.

## Title (EN-US)
Life 20,000 Years Ago: How Humans Survived the Ice Age
(Alternates for A/B in titles.md: #3 and #4.)

## Description (draft)
```
Life 20,000 years ago: Dave's fur coat just blew away, he is standing in a cotton hoodie at the edge of the Ice Age, and he needs to stay alive. How did people actually survive the cold? We bust the biggest myth first (the Ice Age was not ice everywhere), then try five fixes: clothes, fire, a house, food and a crew.

Spoiler: it was never one trick. Which fix would you have trusted?

CHAPTERS
0:00 Intro
0:23 Myth check: was the world frozen?
1:34 Fix 1: Clothes
2:38 Fix 2: Fire
3:36 Fix 3: A house
4:29 Fix 4: Food
5:26 Fix 5: The crew
6:29 The verdict
7:03 Next episode

SOURCES (full list with notes in sources.md)
• Clark et al. (2009), Science 325:710, "The Last Glacial Maximum"
• Tierney et al. (2020), Nature 584:569, "Glacial cooling and climate sensitivity revisited"
• USGS, glacier extent then and now; Lambeck et al. (2014), PNAS, sea level at the Last Glacial Maximum
• Toups et al. (2011), Mol. Biol. Evol. 28:29, origin of clothing lice
• Revedin et al. (2010), PNAS 107:18815, 30,000-year-old plant food processing
• Chu, Shydlovskyi & Maier (2025), Open Research Europe, new radiocarbon dates for the Mezhyrich mammoth-bone structures (Ukraine)
• Cole (2017), Scientific Reports 7:44707, calorie values of Palaeolithic prey (mammoth estimate)
• Villalba-Mouco et al. (2023), Nature Ecology & Evolution, genomes of Solutrean-associated people in Iberia
• Lascaux lamps (French Ministry of Culture, Lascaux "Lighting" page); Pavlovian carnivore skinning marks (Masaryk University summary); antler spear-throwers (Combe Saunière, Isturitz)

Dave's camp is a composite built from several real Ice Age sites (Mezhyrich, Lascaux, Czech Pavlovian sites, French spear-thrower finds), not one camp. Much of what we know about Ice Age daily life is inferred from a thin archaeological record. We say when something is an inference.

This is an animated explainer. Narration: AI voice. Animated with AI-assisted illustrations.

#history #iceage #mammoth
```
(Wording check before upload, items taken only from abstracts or summaries: sources.md #3, #7, #8, #12, #13, #14, #15, #16, #19, #21, #22. Mezhyrich fuel and Lascaux lamps are from news summaries, read the papers first. The 3.5 million calories figure is Cole 2017 as a press-summary number (about 3.6 million), narrated as "by one estimate". Source list must match the studies actually narrated; do not add one that is not in sources.md. Check the "wording check" items first: sources.md #3, #7, #8, #12, #13, #14, #15, #16, #19, #21, #22.)

## Tags
life 20000 years ago, life 20,000 years ago, how did humans survive the ice age, ice age life, ice age humans, ice age explained, woolly mammoth, mammoth bone house, last glacial maximum, was the ice age frozen everywhere, how did ancient humans stay warm, animated history, dave vs history, history explained

## Settings
Category Education · English · Not made for kids · Altered/synthetic content: No, same as EP02-EP04 (stylized animation, not realistic footage) [Likely]: confirm in the Studio form before publish · Playlist: How Did They Do It? (PLAYLISTS Dave, playlist 2) · End screen: EP06 does not exist at upload, so use the latest upload + subscribe, then replace with EP06 once it is live · Pinned comment (draft): "Which fix would you have trusted first: furs, fire, a bone house, or the crew?" (no emoji unless the owner prefers the channel style).

## Thumbnail
Chosen: t3 (mammoth left, frozen Dave right, sunset), text "20,000 YEARS AGO" (3 words, left, yellow and white with dark outline): `thumbnail/final_candidate_t3_20000_years.jpg` (1280x720). Source `thumbnail/src/t3.jpg` is untouched, so the text can be redone in the editor. Final feed-size check next to EP01-EP04 is the owner's.

**Pinned comment (draft):** "Which fix would you have trusted first: furs, fire, a bone house, or the crew?"

## Music
Same track as EP03/EP04: "Science Montage" (Jeremy Blake, YouTube Audio Library); file in `studio/episodes/ep03-restart-humanity/audio/music/`. Mix per studio/tools/mix_music.sh (music about -27 LUFS before ducking, sidechain under the voice, final -14 LUFS).

## Voice (generated 2026-11-20)
vsub "Bill" (pqHfZKP75CvOlQylNhV4), stability 55, similarity 75, style 15, **speed 100**. Generated: 9 sections (s00-s08), 5,376 characters, 535 vsub credits for the long video; 3 Shorts (15 takes, 426 characters) 37 credits. vsub balance 6,774 -> 6,202.

## Shorts (texts in SHORTS.md)
### S1 — `shorts/s1-myth-frozen.mp4` (9.7 s) — hook "ICE AGE = ALL ICE?", images V01-V10, myth bust
Title: Was the Ice Age frozen everywhere? No. #shorts
Description: Ice sheets covered about a quarter of the world's land at the Last Glacial Maximum, against around 11% today. Most of Asia and Africa had no ice sheets at all (Clark et al., 2009; USGS). #history #iceage #shorts
### S2 — `shorts/s2-burn-bones.mp4` (8.2 s) — hook "NO WOOD? NO PROBLEM.", images V12-V21, curiosity fact
Title: No trees? Ice Age hunters may have burned bones. #shorts
Description: At Mezhyrich in Ukraine, hearths held lots of burned bone and almost no wood charcoal. Researchers read this as bone burned for fuel where wood was scarce; whether it was deliberate is still being tested. #history #iceage #shorts
### S3 — `shorts/s3-mammoth-calories.mp4` (8.2 s) — hook "3.5 MILLION CALORIES?", images V23-V32, size shock
Title: One mammoth, about 3.5 million calories? #shorts
Description: By one estimate (Cole, 2017), the muscle of a single mammoth held about 3.6 million calories. A big male stood about 11 feet at the shoulder. #history #iceage #mammoth #shorts
