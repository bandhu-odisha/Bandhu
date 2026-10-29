# e2e d1 r1 (CSS hard-reloaded, ?v=16 confirmed; wrap aspect-ratio computed = auto)

| page | viewport | logo box | natural | ratio box/natural | gallery link (ratio) | img objectFit/box | scrollWidth |
|---|---|---|---|---|---|---|---|
| 2022 | 1280 | 290x232 | 600x480 | 1.000 | 266.6x200.0 (1.333) | contain / same | 1280 |
| 2022 | 390 | 351x280.8 | 358x287 (served variant) | 1.002 | 327.6x245.7 (1.333) | contain / same | 390 |
| 2025 | 1280 | 290x203 | 600x420 | 1.000 | no gallery | - | 1280 |
| 2025 | 390 | 351x245.7 | 358x251 (served variant) | 1.002 | no gallery | - | 390 |

Note: first run had wrap aspect-ratio still 1/1 (my sed hit wrong line); fixed, remeasured.
Screenshots in scratch/: after-2022-1280, after-2022-390, after-2025-1280, after-2025-390.
