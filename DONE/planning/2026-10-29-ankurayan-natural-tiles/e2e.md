# E2E record - Ankurayan natural-shape tiles (build u1 r1)

Server: runserver 127.0.0.1:8011 (local sqlite, 15 Ankurayan records). Browser: chrome-devtools-axi. CSS loaded as `ankurayan.css?v=15`.
Viewport read back via `innerWidth`: 1280 and 390 (emulate 390x844 mobile).

## Cards (img box via getBoundingClientRect; img width = tile - 2px card border)
| width | height all 15 | strip.scrollWidth / clientWidth | docScrollWidth | objectFit |
| --- | --- | --- | --- | --- |
| 1280 | 270 | 7014 / 1140 | 1280 | contain |
| 390 | 225 | 6270 / 390 | 390 | contain |

1280 samples (`--tile-w` -> img box width): 2018 (0.75) 202px -> 200; 2019 (3.48) 939px -> clamped 718 (tile 720); 2.00 ratio 540 -> 538; 2021 (no rendition) none -> 358 (360 default tile). At 390 every img box is 358 x 225, one card per screen (6270 = 15 x 420 - 30).

## Hero (img src swapped to /static/img/our_mission1.jpg, natural 1600x1067 = 1.4995)
| width | card box | ratio | aspect-ratio | docScrollWidth |
| --- | --- | --- | --- | --- |
| 1280 | 336 x 224.06 | 1.4996 | auto | 1280 |
| 390 | 336 x 224.06 | 1.4996 | auto | 390 |

## Motion (round 2: Gallery behavior, no arrows, no reduced-motion gate, matchMedia NOT stubbed)
This Chrome reports `prefers-reduced-motion: reduce` = true; the timer still runs (always on, like Gallery).
- 1280: scrollLeft advanced 1388 -> 1778 in 2.6s; over 48s it ran 3195 ... 5874 (max), wrapped to 0, then 300, 716, 1020.
- Hover (mouseenter on wrap): frozen 4.5s. Focus (strip.focus()) then mouseenter+mouseleave while still focused: frozen 4.5s. After blur: resumed within 4.5s.
- Arrows: `[data-strip-dir], .glide__arrow` count on the home page = 0 at 1280 and 390; strip has role=region.
- Hero: `body.ankurayan-page` rules alone give aspect-ratio auto at 390 after deleting the <=768px duplicate block.

## Measurements (r2)
| width | img heights (15) | docScrollWidth == innerWidth |
| --- | --- | --- |
| 1280 | 270 | 1280 yes |
| 390 | 225 | 390 yes |

Screenshots: scratch/desktop-1280.png, scratch/phone-390.png.
