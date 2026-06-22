# Spec: Data-Driven Landing Page Carousel

## Objective

**Problem:** Slide images, titles, subtitles, and captions on the landing page are hardcoded in React JSX files. Any content update requires a code change + Vite rebuild + deployment. This creates unnecessary coupling between content and code.

**Goal:** Make all landing page carousel content (images + copy) fully manageable via Django admin — no code change needed to update slides.

**Users:**
- **Content editors** (non-technical staff): update hero slides, about photos, mission images from Django admin
- **Developers**: zero-friction architecture where content and code are decoupled

**Success:** A content editor can add/remove/reorder a hero slide (image + title + subtitle) entirely from `/admin/` with no code change, rebuild, or redeployment required.

---

## Scope — Three Carousel Locations

| Section | Component | Current State | Problem |
|---|---|---|---|
| **Hero** | `Hero.jsx` | `HERO_SLIDES[]` hardcoded titles/subtitles; `HERO_FALLBACK_IMAGES[]` hardcoded image paths | Content requires code change |
| **About** | `About.jsx` | `DEFAULT_ABOUT_SLIDES[]` hardcoded captions + image paths; merges with `data.about_slides` if present (already partially data-driven) | Fallback still hardcoded; captions not DB-managed |
| **Mission pillars** | `Mission.jsx` | Only `index[0]` of `{pillar}_images[]` displayed; multiple images exist in DB but unused; fallback images hardcoded | Multi-image carousel not implemented; images not rotated |

**Out of scope:** Gallery auto-scroll (already data-driven), `Our Visitors` carousel (already data-driven).

---

## Tech Stack

- **Backend:** Django (existing) — model changes + migration + admin registration
- **Frontend:** React 18 + Vite + Tailwind CSS (existing)
- **Transport:** existing `_build_landing_data()` JSON-blob SSR pattern — no new endpoints
- **No new runtime dependencies** — zero new packages added

---

## Commands

```bash
# Frontend build
cd frontend && npm run build

# Frontend dev with hot reload
cd frontend && npm run dev

# Django migrations
python manage.py makemigrations bandhuapp
python manage.py migrate

# Seed / verify
python manage.py runserver
```

---

## Architecture: How Data Flows

```
Django Admin
  └── HeroSlide (image, title, subtitle, order)
        │
        ▼
  _build_landing_data()           ← bandhuapp/views.py
  → data['hero_slides'] = [       ← NEW field in JSON blob
      { image_url, title,
        subtitle, order },
      ...
    ]
        │
        ▼
  landing_react.html
  {{ landing_data|json_script:"landing-data" }}
        │
        ▼
  App.jsx → Hero.jsx
  data.hero_slides[]              ← replaces HERO_SLIDES[] + HERO_FALLBACK_IMAGES[]
```

Same pattern for About slides and Mission pillar carousel (already partially wired).

---

## Project Structure

```
bandhuapp/
  models.py          ← ADD: HeroSlide model
  admin.py           ← ADD: HeroSlideAdmin
  views.py           ← MODIFY: _build_landing_data() → populate hero_slides[]
  migrations/
    0022_heroslide.py  ← NEW migration

frontend/src/components/
  Hero.jsx           ← MODIFY: read data.hero_slides, remove HERO_SLIDES constant
  About.jsx          ← MODIFY: remove DEFAULT_ABOUT_SLIDES fallback constant
  Mission.jsx        ← MODIFY: show all images[] per pillar, not just index[0]
```

---

## Data Model Changes

### New: `HeroSlide`

```python
class HeroSlide(models.Model):
    image         = models.ImageField(upload_to='bandhuapp/hero')
    title         = models.CharField(max_length=120)
    subtitle      = models.TextField(max_length=400, blank=True)
    order         = models.PositiveSmallIntegerField(default=0)
    is_active     = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Hero Slide'
        verbose_name_plural = 'Hero Slides'
```

`transition_ms` is **not** added — slide interval stays as `HERO_SLIDE_MS = 6000` in `Hero.jsx` (acceptable hardcode per spec agreement).

### Existing: `SanskarCarousel`, `SwarajCarousel`, `SwabalambanCarousel`

Already have `picture` + FK to `Mission`. **No schema change needed.** Only `views.py` and `Mission.jsx` need updating to pass and consume all images (not just `[0]`).

### Existing: `About` section slides

`_build_landing_data()` already populates `data['about_slides']` from `resolve_media_or_static()`. The About.jsx fallback `DEFAULT_ABOUT_SLIDES[]` should be removed once the DB has content. **No schema change needed** — just clean up the React fallback after seeding.

---

## Code Reduction: What Gets Deleted

This is a net-reduction feature. The DB model adds ~15 lines; the deletions are larger.

### `frontend/src/components/Hero.jsx` — delete ~30 lines

| What gets removed | Lines | Why |
|---|---|---|
| `HERO_FALLBACK_IMAGES = [...]` constant (4 hardcoded paths) | 6 | Replaced by DB images; true fallback stays as a minimal 1-image safety net |
| `HERO_SLIDES = [...]` constant (4 titles + subtitles) | 22 | Replaced by `data.hero_slides[]` from Django |
| `collectHeroImages()` function + its `useMemo` call | 14 | No longer needed — slides come pre-assembled from `_build_landing_data()` |
| `importedImages` → zip-with-`HERO_SLIDES` logic in `useMemo` | 8 | Replaced by `const slides = data.hero_slides ?? HERO_FALLBACK_SLIDES` |

**Net: ~50 lines removed, ~5 lines added.** `Hero.jsx` shrinks from ~200 to ~155 lines.

**Before:**
```js
const HERO_FALLBACK_IMAGES = ['/static/img/our_mission.jpg', ...]   // 6 lines
const HERO_SLIDES = [{ title: '...', subtitle: '...' }, ...]        // 22 lines

function collectHeroImages(data) { ... }                             // 14 lines

const importedImages = useMemo(() => collectHeroImages(data), [data])
const slides = useMemo(
  () => HERO_SLIDES.map((slide, i) => ({
    ...slide,
    image: importedImages[i] || HERO_FALLBACK_IMAGES[i] || null,
  })),
  [importedImages]
)
```

**After:**
```js
const HERO_FALLBACK_SLIDES = [{ image: '/static/img/our_mission.jpg', title: 'Bandhu', subtitle: '' }]

const slides = data?.hero_slides?.length ? data.hero_slides : HERO_FALLBACK_SLIDES
```

---

### `bandhuapp/views.py` — delete ~35 lines inside `_build_landing_data()`

| What gets removed | Lines | Why |
|---|---|---|
| `about_slide_specs` tuple + loop populating `data['about_slides']` | 10 | Replaced by `AboutSlide` DB query (or kept if About slides stay file-based) |
| `hero_extra_specs` tuple + loop populating `data['hero_photos']` | 8 | Replaced by `HeroSlide.objects.filter(is_active=True)` |
| `reserved_gallery_names` set-building from both spec tuples | 10 | The reservation logic that exists solely to prevent hero images from leaking into the gallery grid becomes unnecessary once hero images live in their own model |
| `data['hero_photos']` key entirely removed | 1 | Replaced by `data['hero_slides']` |

**Net: ~29 lines removed, ~6 lines added.**

**Before:**
```python
hero_extra_specs = (
    ('bandhuapp/swaraj/our_mission1.jpg', 'our_mission1.jpg'),
    ('bandhuapp/gallery/about-slide-3-campus.png', 'about-slide-3-campus.png'),
    ('bandhuapp/gallery/about-slide-blossoms.png', 'about-slide-blossoms.png'),
)
reserved_gallery_names = {
    os.path.basename(p).lower() for p, _ in hero_extra_specs
}
reserved_gallery_names.add('our_mission.jpg')
data['hero_photos'] = []
for relative_path, static_name in hero_extra_specs:
    hero_url = resolve_media_or_static(relative_path, static_name)
    if hero_url:
        data['hero_photos'].append({'picture': hero_url})
```

**After:**
```python
data['hero_slides'] = [
    {'image': file_url(s.image), 'title': s.title, 'subtitle': s.subtitle}
    for s in HeroSlide.objects.filter(is_active=True)
]
```

---

### Total reduction across both files

| File | Lines removed | Lines added | Net |
|---|---|---|---|
| `Hero.jsx` | ~50 | ~5 | **−45** |
| `views.py` | ~29 | ~6 | **−23** |
| `models.py` | 0 | ~18 | +18 |
| `admin.py` | 0 | ~8 | +8 |
| `migration` | 0 | ~20 | +20 |
| **Total** | **~79** | **~57** | **net −22 lines** |

The codebase gets *smaller*, not larger. Every removed line was content masquerading as code.



Match existing patterns exactly:

```python
# models.py — follow existing carousel pattern
class HeroSlide(models.Model):
    image = models.ImageField(upload_to='bandhuapp/hero')
    title = models.CharField(max_length=120)
    subtitle = models.TextField(max_length=400, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
```

```python
# views.py — follow existing mission_carousel() pattern
data['hero_slides'] = [
    {
        'image': file_url(slide.image),
        'title': slide.title,
        'subtitle': slide.subtitle,
    }
    for slide in HeroSlide.objects.filter(is_active=True)
]
```

```jsx
// Hero.jsx — remove HERO_SLIDES[] constant; read from data prop
const slides = data?.hero_slides?.length ? data.hero_slides : HERO_FALLBACK_SLIDES
```

---

## Testing Strategy

No test framework currently exists in the project. Manual verification plan:

1. Add a `HeroSlide` record in Django admin with image + title + subtitle
2. Load `/` — confirm the new slide appears in the Hero carousel
3. Remove all `HeroSlide` records — confirm fallback static slides still render (no blank/broken state)
4. Add multiple `SanskarCarousel` images in admin — confirm Mission section cycles through all of them
5. Reorder `HeroSlide` records via `order` field — confirm carousel respects the order
6. Set `is_active=False` on a slide — confirm it disappears without code change

---

## Boundaries

- **Always:** Preserve existing `HERO_FALLBACK_SLIDES` (renamed from `HERO_FALLBACK_IMAGES`) as a safety net — the page must never be blank if DB has no slides
- **Always:** Follow the existing `_build_landing_data()` pattern — all data via JSON blob, no new AJAX endpoints
- **Always:** Run `npm run build` after any JSX changes; confirm `static/frontend/assets/index.js` is updated
- **Ask first:** Any schema change beyond `HeroSlide` (e.g. adding `caption` to `SanskarCarousel`)
- **Ask first:** Adding drag-and-drop reorder UI in admin (out of scope for now; `order` integer field is sufficient)
- **Never:** Remove the static fallback images from `static/img/` — they're referenced across templates
- **Never:** Add an external carousel library (Swiper, Embla, etc.) — zero new runtime deps
- **Never:** Commit `static/frontend/assets/` to git — build artifacts belong in the deploy pipeline, not version control. Add this directory to `.gitignore`.
- **Never:** Change `HERO_SLIDE_MS` or any carousel timing constant in JSX for a content update — timing is a DB field (`transition_ms` on `HeroSlide`), not a code constant

---

## Success Criteria

- [ ] A `HeroSlide` record added in Django admin appears as a slide on `/` without any code change or rebuild
- [ ] Hero carousel title and subtitle are driven by DB fields, not JSX constants
- [ ] Mission pillar sections cycle through all uploaded images (not just index[0])
- [ ] `About.jsx` uses `data.about_slides` from Django; hardcoded `DEFAULT_ABOUT_SLIDES` constant is removed
- [ ] If no DB slides exist, page renders without errors using static fallbacks
- [ ] `HERO_SLIDES` constant (hardcoded copy) is deleted from `Hero.jsx`

---

## Open Questions

1. ~~Should `HeroSlide` have a `caption` field?~~ **Resolved:** `title` + `subtitle` only. No caption field.
2. ~~Mission pillar images: timer or interaction?~~ **Resolved:** Timer, 6000ms, hardcoded constant is acceptable for pillar carousel. `transition_ms` DB field is Hero-only.
3. Do `SanskarCarousel` / `SwarajCarousel` / `SwabalambanCarousel` need `title`/`caption` fields? **Deferred** — implement image-only carousel for pillars now; caption fields can be added in a follow-up migration if needed.
4. ~~Seed command for initial data?~~ **Resolved:** Yes — write a `seed_hero_slides` management command to bootstrap the DB with current hardcoded `HERO_SLIDES` copy so no data is lost on first migration.
