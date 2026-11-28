# Hook guide (2026-11-28)

Built from the first 35 s of 13 rival videos that beat their channel (topic_radar ratios), transcripts in
youtube-transcript/ (not committed), and our own retention reads (docs/script-rules.md). Use it for every new script,
together with tools/hook_check.py. Never bend a fact to make a hook.

## What the winners open with
| Video (ratio) | First sentence does | Then |
|---|---|---|
| Florida Big Bend (219x) | contrast: Florida grows fastest, most newcomers go to the coast | "But" one curve got skipped + 3 concrete oddities (no beaches, rivers vanish underground, biggest town ~1,000) + 2 story teasers (a baron's vow, 4 hurricanes in 3 years) -> question at ~0:22 |
| Northern Ontario "hiding" (8.8x) | a crime: richest man found beaten, burned, covered in feathers, 1943 | stack of wonders (a hole so deep its water has not seen sky in a billion years) -> a stake that is live today (a court case right now) |
| Why nobody lives in N. Ontario (Forgotten Canada) | one micro-story: a town selling lots at 90 % off, $500 | the mill that was its only reason to exist closed on a named date |
| Geoff, Africa's coast (3.5x) | two famous cities, then "2,000 miles of absolutely nothing" between them | question by 0:20 |
| Greenland (Glore) | myth-bust: "and no, it's not the cold" | proof against the myth (Alaska, Iceland are as cold), then the question |
| 13 towns N. Ontario (24x) | an extreme specific: a town where the census counted exactly five people | scale against something known (larger than France + Germany) |
| Akpatok (14.8x) | "Have a look at this" on the picture + a quote: "Nobody lands on Akpatok" | a 100-year-old mystery |

## Rules for our scripts (from episode 2026-12 on)
1. **Sentence one is a person, an event or a strange exact detail, not a general scale fact.** The scale fact
   ("a quarter of the state, bigger than ...") moves to sentence two or three. Pick the strongest true moment of the
   whole video (a disaster, a crime, a reversal) and say it in one sentence with a date or number.
2. **Contrast before the "But":** what everyone expects or what happens everywhere else, then the place that breaks it.
3. **Three teasers with concrete nouns**, each a small story with stakes, and at least one that is **still live
   today** (a court case, a vote, a project, a boom).
4. **Myth-bust when there is an obvious wrong answer** ("it is not the cold / not the desert"): name it, knock it down
   with one comparison.
5. **The question aloud by 0:25** (hook_check QUESTION), then one line of promise, then straight into the first story.
6. **The first picture shows the first sentence** (the event or the person), not a wide map; the cover's map view comes
   at the question.
7. **0:30-2:30 has no lecture:** the first reason opens on a story (a person, a date) and the hook's open loop stays
   open until at least 2:30.
8. Write five openings in this guide's patterns, score them with hookscore.py / hook_check.py, keep the best; record the
   choice and the 0:30 / 0:45 retention in the episode's retention.md once the video has 50+ views.

## Example (Northern Idaho, written after the render; for comparison)
Ours: "Northern Idaho is a quarter of the state, a block of mountains and forest bigger than Vermont and New Hampshire
put together."
Guide version: "In 1974, the children of one Idaho mining town had some of the highest blood lead levels ever measured
in America. The town sits in the emptiest part of the state. Northern Idaho is a quarter of Idaho, bigger than
Vermont and New Hampshire together, yet only one Idahoan in five lives there."
