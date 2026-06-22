# Implementation Plan: Data-Driven Landing Page Carousel

## Overview

Replace hardcoded slide content in `Hero.jsx`, `About.jsx`, and `Mission.jsx` with DB-managed content served via the existing `_build_landing_data()` JSON-blob pattern. Three vertical slices: Hero slides (new model), About slides (cleanup), Mission pillar carousel (wire existing data). Net result: ~22 fewer lines of code, zero new dependencies, content editors never touch code again.

---

## Architecture Decisions

- **No new endpoints** — all data flows through the existing `_build_landing_data()` → `json_script` SSR pattern
- **`HeroSlide` is a standalone model** (not inlined under `HomePage`) — cleaner admin, independent ordering
- **Mission carousel uses existing DB models** (`SanskarCarousel` etc.) — no schema change, just pass all images not just `[0]`
- **About fallback stays minimal** — `DEFAULT_ABOUT_SLIDES` reduced to a single-slide safety net; `data.about_slides` is already the primary path
- **Seed command for Hero** — preserves current hardcoded copy as initial DB records, no content lost on first migration

---

## Dependency Graph

```
Task 1: HeroSlide model + migration
    │
    ├── Task 2: admin registration (depends on model)
    │
    ├── Task 3: seed_hero_slides command (depends on model)
    │       ↑ run before Task 4 in dev
    │
    └── Task 4: views.py — add hero_slides to JSON blob (depends on model)
            │
            └── Task 5: Hero.jsx — read data.hero_slides, delete constants (depends on Task 4 data shape)

Task 6: Mission.jsx — pass all pillar images (depends on existing views.py data, no model change)

Task 7: About.jsx — remove DEFAULT_ABOUT_SLIDES (depends on about_slides already in JSON blob — verified working)
```

Tasks 1–5 are sequential (Hero vertical slice).
Tasks 6 and 7 are independent of each other and of Tasks 1–5 (can be done in any order after checkpoint).

---

## Phase 1: Hero Slides (Backend Foundation)

### Task 1: Add `HeroSlide` model and migration

**Description:** Add the `HeroSlide` model to `bandhuapp/models.py` and generate migration `0022_heroslide.py`. This is the foundation everything else depends on.

**Acceptance criteria:**
- [ ] `HeroSlide` model has fields: `image (ImageField)`, `title (CharField 120)`, `subtitle (TextField 400 blank)`, `order (PositiveSmallIntegerField default=0)`, `is_active (BooleanField default=True)`
- [ ] `Meta.ordering = ['order']`
- [ ] Migration `0022_heroslide.py` exists and applies cleanly: `python manage.py migrate` exits 0

**Verification:**
```bash
python manage.py migrate
python manage.py shell -c "from bandhuapp.models import HeroSlide; print(HeroSlide._meta.fields)"
```

**Dependencies:** None

**Files touched:**
- `bandhuapp/models.py`
- `bandhuapp/migrations/0022_heroslide.py`

**Size:** S

---

### Task 2: Register `HeroSlideAdmin`

**Description:** Register `HeroSlide` in `bandhuapp/admin.py` so content editors can manage slides immediately after migration.

**Acceptance criteria:**
- [ ] `HeroSlide` is visible at `/admin/bandhuapp/heroslide/`
- [ ] `list_display = ('order', 'title', 'is_active', 'image')`
- [ ] `list_editable = ('order', 'is_active')` — inline reordering in the list view
- [ ] `ordering = ('order',)`

**Verification:**
```bash
python manage.py runserver
# Open /admin/bandhuapp/heroslide/ — confirm list and add form work
```

**Dependencies:** Task 1

**Files touched:**
- `bandhuapp/admin.py`

**Size:** XS

---

### Task 3: `seed_hero_slides` management command

**Description:** Create `bandhuapp/management/commands/seed_hero_slides.py` that bootstraps the DB with the 4 slides currently hardcoded in `Hero.jsx`. Uses `get_or_create` (idempotent). Copies images from `static/img/` to `MEDIA_ROOT/bandhuapp/hero/`.

**Acceptance criteria:**
- [ ] `python manage.py seed_hero_slides` runs without error on empty DB
- [ ] Running it twice is safe (idempotent — no duplicate records)
- [ ] After running: `HeroSlide.objects.count() == 4`
- [ ] Each slide has the title/subtitle from the current `HERO_SLIDES[]` constant in `Hero.jsx`

**Verification:**
```bash
python manage.py seed_hero_slides
python manage.py shell -c "from bandhuapp.models import HeroSlide; print(list(HeroSlide.objects.values('order','title','is_active')))"
```

**Dependencies:** Task 1

**Files touched:**
- `bandhuapp/management/commands/seed_hero_slides.py` (new file)

**Size:** S

---

### ✅ Checkpoint A — Backend foundation

Before proceeding to Task 4:
- [ ] `python manage.py migrate` exits 0
- [ ] `python manage.py seed_hero_slides` exits 0 and creates 4 records
- [ ] `/admin/bandhuapp/heroslide/` shows the 4 seeded slides
- [ ] **Human review:** confirm slide titles/subtitles look right in admin

---

## Phase 2: Hero Slides (Wire to Frontend)

### Task 4: `_build_landing_data()` — add `hero_slides`, remove `hero_extra_specs`

**Description:** Update `bandhuapp/views.py` to query `HeroSlide` and populate `data['hero_slides']`. Remove `hero_extra_specs`, `reserved_gallery_names` (the workaround), and `data['hero_photos']` — these exist solely because hero images were stored alongside gallery images.

**Acceptance criteria:**
- [ ] `data['hero_slides']` is a list of `{image, title, subtitle}` dicts ordered by `HeroSlide.order`
- [ ] `hero_extra_specs` tuple is deleted
- [ ] `reserved_gallery_names` set-building block is deleted (or reduced to only what's still needed for `about_slide_specs`)
- [ ] `data['hero_photos']` key removed
- [ ] `GET /api/landing/` response contains `hero_slides` key with correct data
- [ ] Gallery grid still excludes about-slide images (the `about_slide_specs` reservation stays)

**Verification:**
```bash
python manage.py runserver
curl http://localhost:8000/api/landing/ | python -m json.tool | grep -A 20 '"hero_slides"'
# Confirm 4 slides with image URLs, titles, subtitles
```

**Dependencies:** Task 1, Task 3 (seed data in DB)

**Files touched:**
- `bandhuapp/views.py`

**Size:** S

---

### Task 5: `Hero.jsx` — read `data.hero_slides`, delete hardcoded constants

**Description:** Update `Hero.jsx` to read slides from `data.hero_slides`. Delete `HERO_SLIDES[]`, `HERO_FALLBACK_IMAGES[]`, `collectHeroImages()`, and the zip-merge `useMemo`. Keep a minimal `HERO_FALLBACK_SLIDES` (single slide) as a safety net for empty DB.

**Acceptance criteria:**
- [ ] `HERO_SLIDES` constant deleted
- [ ] `HERO_FALLBACK_IMAGES` constant deleted
- [ ] `collectHeroImages()` function deleted
- [ ] `const slides = data?.hero_slides?.length ? data.hero_slides : HERO_FALLBACK_SLIDES`
- [ ] Hero carousel renders the 4 DB slides with correct titles and images at `http://localhost:3000`
- [ ] With `HeroSlide.objects.all().delete()` in shell: page still renders with fallback (no blank/crash)
- [ ] `npm run build` exits 0

**Verification:**
```bash
cd frontend && npm run build
# Load / in browser — confirm 4 slides cycle with correct DB titles
python manage.py shell -c "from bandhuapp.models import HeroSlide; HeroSlide.objects.all().delete()"
# Reload / — confirm fallback slide renders, no crash
```

**Dependencies:** Task 4

**Files touched:**
- `frontend/src/components/Hero.jsx`
- `static/frontend/assets/index.js` (rebuilt artifact — NOT committed to git)

**Size:** S

---

### ✅ Checkpoint B — Hero slice complete (end-to-end)

- [ ] `npm run build` exits 0
- [ ] `python manage.py runserver` + open `/` — Hero carousel shows DB-driven slides
- [ ] Add a new `HeroSlide` in admin → reload `/` → new slide appears (no rebuild)
- [ ] Set `is_active=False` on a slide → reload `/` → slide gone
- [ ] Change `order` values → reload → sequence changes
- [ ] Delete all slides → fallback renders, no error
- [ ] **Human review before proceeding to Phase 3**

---

## Phase 3: Mission Pillar Carousel

### Task 6: `Mission.jsx` — cycle all pillar images, not just `[0]`

**Description:** Each pillar (`sanskar`, `swaraj`, `swabalamban`) already has multiple images in the DB (`{pillar}_images[]` array in the JSON blob). `Mission.jsx` currently calls `getImage(imgs) => imgs[0]` and discards the rest. Replace the single static image with an auto-advancing carousel using the same `setInterval` pattern already used in `Hero.jsx` and `About.jsx`.

**Acceptance criteria:**
- [ ] `getImage()` helper deleted
- [ ] Each pillar renders all its images as an auto-advancing slideshow (6000ms, same as Hero)
- [ ] Hardcoded `fallbackImages` object in `Mission.jsx` reduced to single-image safety net per pillar
- [ ] If a pillar has only 1 image, no timer is started (matches existing pattern in `Hero.jsx`)
- [ ] No new dependencies added

**Verification:**
```bash
# In admin: add 2+ images to Sanskar carousel
# Load / and navigate to #pillars — confirm Sanskar image cycles
# With 1 image only: confirm no flicker/timer
```

**Dependencies:** None (existing DB data + existing JSON blob shape already correct)

**Files touched:**
- `frontend/src/components/Mission.jsx`

**Size:** S

---

## Phase 4: About Slides Cleanup

### Task 7: `About.jsx` — remove `DEFAULT_ABOUT_SLIDES` constant

**Description:** `About.jsx` already reads `data.about_slides` from the JSON blob (partially wired). The `DEFAULT_ABOUT_SLIDES` constant (5 hardcoded slides with captions) is only used as a fallback when `data.about_slides` is empty. Replace with a minimal single-slide fallback. The `about_slide_specs` in `views.py` already populates `data.about_slides` from `resolve_media_or_static()` — verify it works, then remove the hardcoded constant.

**Acceptance criteria:**
- [ ] `DEFAULT_ABOUT_SLIDES` constant (45 lines) deleted from `About.jsx`
- [ ] Fallback is a single minimal slide: `[{ src: '/static/img/about-slide-1-gardenia.png', caption: '' }]`
- [ ] About section renders correctly when `data.about_slides` is populated (primary path)
- [ ] About section renders the fallback when `data.about_slides` is empty (safety net)

**Verification:**
```bash
# Load / — About section shows images correctly
python manage.py shell -c "
from bandhuapp.views import _build_landing_data
from django.test import RequestFactory
r = RequestFactory().get('/')
d = _build_landing_data(r)
print('about_slides count:', len(d.get('about_slides', [])))
"
```

**Dependencies:** None (verify `data.about_slides` is populated before deleting fallback)

**Files touched:**
- `frontend/src/components/About.jsx`

**Size:** XS

---

### ✅ Checkpoint C — All three carousels data-driven

- [ ] `npm run build` exits 0
- [ ] Hero: DB-driven, fallback works, no hardcoded constants
- [ ] Mission pillars: all images cycle (not just index[0])
- [ ] About: `DEFAULT_ABOUT_SLIDES` constant gone, `data.about_slides` is primary
- [ ] `git diff --stat` shows net line reduction (more deletions than additions)
- [ ] **Final human review**

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| `hero_extra_specs` images were also used as gallery-reservation guards | Med | Audit `reserved_gallery_names` after removal — ensure `about_slide_specs` reservation still excludes about images from gallery grid |
| `data['hero_photos']` key removal breaks Hero.jsx before Task 5 is done | Med | Do Task 4 and Task 5 in the same session — don't deploy between them |
| Seeded hero slide images not found at media path | Low | Seed command copies files to MEDIA_ROOT; fallback renders static path if copy fails |
| Mission pillar carousel flickers with 1 image | Low | Guard: `if (images.length <= 1) return undefined` in useEffect (same as Hero pattern) |

---

## Parallelization

- Tasks 1, 2, 3 can be done in one session (all backend, fast)
- Task 6 (Mission) and Task 7 (About) are independent of Tasks 1–5 and of each other
- **Must be sequential:** Task 4 before Task 5 (data shape must exist before JSX reads it)
