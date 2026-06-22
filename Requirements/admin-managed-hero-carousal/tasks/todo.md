# Todo: Data-Driven Landing Page Carousel

## Phase 1 — Backend Foundation

- [x] **Task 1** · `HeroSlide` model + migration `0022_heroslide.py`
- [x] **Task 2** · `HeroSlideAdmin` registration
- [x] **Task 3** · `seed_hero_slides` management command
- [x] **✅ Checkpoint A** — admin shows 4 seeded slides → human confirmed

## Phase 2 — Hero Frontend Slice

- [x] **Task 4** · `_build_landing_data()` — add `hero_slides`, remove `hero_extra_specs` + `reserved_gallery_names` + `hero_photos`
- [x] **Task 5** · `Hero.jsx` — delete `HERO_SLIDES`, `HERO_FALLBACK_IMAGES`, `collectHeroImages()`, zip-merge logic
- [x] **✅ Checkpoint B** — full Hero end-to-end working → human confirmed

## Phase 3 — Mission Pillar Carousel

- [x] **Task 6** · `Mission.jsx` — `PillarCarousel` component, cycles all images with 6s timer

## Phase 4 — About Slides Cleanup

- [x] **Task 7** · `About.jsx` — `DEFAULT_ABOUT_SLIDES` (27 lines) deleted → 3-line `ABOUT_FALLBACK_SLIDES`

## Final

- [x] **✅ Checkpoint C** — all 3 carousels data-driven, `npm run build` passes, Django check clean
- [x] `static/frontend/assets/` in `.gitignore` + untracked from git
- [x] Zero references to deleted constants remain in codebase
