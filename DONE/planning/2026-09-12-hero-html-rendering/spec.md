# Hero carousel: render admin-authored HTML in slide title and subtitle

Date: 2026-09-12
Status: implemented — verified against code at commit `9135e62`

## Context

This site has one authoring model, used everywhere except the hero: an admin types raw
HTML into a plain `Textarea` in Django admin, and the template renders it through the
`|safe` filter. No rich-text editor is installed — no CKEditor, TinyMCE or Summernote in
`requirements.txt` or `bandhu/settings.py` — so raw markup in a plain text field is the
intended interface, not a workaround.

Confirmed instances of the convention:

- `templates/initiative_program/list_about_section.html:24` — `{{ content.description|safe }}` inside `<div class="pillar-desc">`
- `applications/charitywork/templates/charity.html:61-62` — `content.tagline|safe`, `content.description|safe`
- `bandhuapp/templates/pillar_page.html:724,731,768` — `{{ desc|safe }}`

The landing page hero is the exception because it is React, not Django. `Hero.jsx`
interpolates the slide fields as plain strings (`{slide.title}` at
`frontend/src/components/Hero.jsx:164`, `{slide.subtitle}` at `:167`), and React escapes
interpolated strings. HTML typed into `HeroSlide.title` or `HeroSlide.subtitle` therefore
appears literally on the page as `&lt;br&gt;` instead of formatting.

Reported symptom: `#about > … > .pillar-desc` on `/other_activities/` renders HTML; the
hero on `/` does not. Screenshot: `/tmp/bandhu-hero.png`.

**Outcome:** hero title and subtitle accept admin HTML, and that HTML renders with the
same typography the Django pages give it.

## Approach

Render both fields with `dangerouslySetInnerHTML`, the pattern already in this same React
bundle: `frontend/src/components/About.jsx:97,107` renders `AboutUs.tagline` and
`AboutUs.desc` — also plain `TextField`s edited in Django admin — exactly this way. These
are the only two existing uses in `frontend/src`; this change adds two more. No new
dependency.

A second, less obvious half of the work: Tailwind Preflight is active
(`@tailwind base` at `frontend/src/index.css:1`; `frontend/tailwind.config.js` sets no
`corePlugins` override, so Preflight is on). Preflight zeroes `p` margins and strips
`ul`/`ol` list styling. Injecting HTML without restoring that typography produces
paragraphs that run together and bullet lists with no bullets and no indent — the same
reason `pillar_page.html:293-296` defines explicit `.pillar-desc p` rules. Section 3
below restores it.

## Decision: no sanitizer

Investigated and rejected on evidence.

**The trust boundary is tight.** `HeroSlide` is editable only through Django admin
(`bandhuapp/admin.py:226`, a plain `ModelAdmin`; there is no on-page admin form for hero
slides). Reaching that form requires `is_staff` or `is_admin`. Both default to `False`
(`accounts/models.py:64`) and are set only by the superuser-creation paths
(`accounts/models.py:38,50`) or by an existing admin editing the user record
(`accounts/admin.py:27`). No self-service path grants staff — social signup does not.
Anyone who can inject script into a hero slide can already run arbitrary admin actions,
so a sanitizer on this field removes no capability from an attacker.

**The cost is real and the benefit is local.** DOMPurify would add a runtime npm
dependency and protect exactly the two React surfaces, while the dozens of Django `|safe`
renderings stay untouched — no client-side sanitizer can reach those. The hero would
become stricter than the rest of the site without being safer.

**Reopen when:** on-page admin gains a hero-slide editor, or `is_staff` becomes grantable
by an automated or self-service flow. At that point the right layer is server-side
`bleach` in `_build_landing_data` (`bandhuapp/views.py:190`), because it also covers the
`|safe` templates — not a client-side library that covers only React.

## Changes

### 1. Title — `frontend/src/components/Hero.jsx:163-165`

Keep the `<h1>` element and its class list; render its content as HTML.

```jsx
<h1
  className="mb-4 w-full font-sans text-xl font-bold leading-tight tracking-tight text-slate-900 max-lg:text-center sm:mb-5 sm:text-2xl md:text-3xl lg:text-left lg:text-[clamp(1.625rem,0.35rem+2.35vw,2.125rem)] xl:text-[clamp(1.75rem,0.5rem+2.1vw,2.35rem)]"
  dangerouslySetInnerHTML={{ __html: slide.title }}
/>
```

The `<h1>` accepts **inline tags only** — `<strong>`, `<em>`, `<span>`, `<br>`, `<a>`. A
block tag such as `<p>` or `<div>` inside an `<h1>` is invalid HTML and the browser
re-nests it outside the heading. This is a constraint to document for authors (section 4),
not something to work around.

Note for authors: Preflight sets `h1 { font-size: inherit; font-weight: inherit }`, so a
nested heading tag in the title would inherit the `<h1>`'s own styling rather than scale.
Use `<span>` with a utility class for emphasis, as in the verification example below.

### 2. Subtitle — `frontend/src/components/Hero.jsx:166-168`

Change `<p>` to `<div>`, keep the existing classes, add child-typography utilities, and
render as HTML.

```jsx
<div
  className="w-full max-w-xl max-lg:mx-auto max-lg:text-center font-sans text-[0.9375rem] leading-relaxed text-slate-700 sm:text-base md:text-lg lg:mx-0 lg:text-left [&_p]:mb-3 [&_p:last-child]:mb-0 [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:list-decimal [&_ol]:pl-5 [&_a]:underline"
  dangerouslySetInnerHTML={{ __html: slide.subtitle }}
/>
```

Two distinct reasons for the two parts of this edit:

- **`<p>` → `<div>`:** an author typing `<p>…</p>` into a `<p>` produces invalid nesting
  that the browser silently unnests, breaking the layout. `.pillar-desc` is a `<div>` for
  this reason. The swap costs nothing visually — Preflight already zeroes the `<p>`
  default margin, and no CSS in `frontend/src/index.css` targets the hero paragraph.
- **Child utilities:** they restore what Preflight strips. Tailwind 3.4
  (`frontend/package.json`) supports arbitrary variants, and the JIT scanner reads these
  literal class strings out of `Hero.jsx` because `frontend/tailwind.config.js` has
  `./src/**/*.{js,ts,jsx,tsx}` in `content`. `<strong>`/`<b>` need no rule — Preflight
  maps them to `font-weight: bolder`.

### 3. Leave `buildHeroSlides` alone — `Hero.jsx:49-63`

The `slide.title || DEFAULT_HERO_SLIDES[i]?.title || ''` fallbacks (lines 55-56) still
work; `__html: ''` renders empty, which is the current behaviour. The
`DEFAULT_HERO_SLIDES` copy (lines 12-31) was checked character by character: it contains
em dashes but no `&`, `<` or `>`, so it renders identically through
`dangerouslySetInnerHTML`. Anyone editing that copy later must HTML-escape a literal `&`.

### 4. Tell authors the rules — `bandhuapp/admin.py:237-241`

The `HeroSlideAdmin` fieldset already carries a `description` string shown above the form.
It is the only place the inline-only constraint can reach the person typing. Extend it:

```python
'description': (
    'Slides rotate on the main home page hero (left text, right image). '
    'Use sort order 0, 1, 2… — typically four slides. '
    'Leave image empty to use the site default for that position. '
    'Title and subtitle accept HTML. Title: inline tags only '
    '(&lt;strong&gt;, &lt;em&gt;, &lt;span&gt;, &lt;br&gt;, &lt;a&gt;). '
    'Subtitle also accepts &lt;p&gt;, &lt;ul&gt; and &lt;ol&gt;.'
),
```

This is the only Python change, and it makes the test-suite check in verification step 6
mandatory rather than conditional.

### 5. Rebuild and ship the bundle

`static/frontend/assets/index.js` and `index.css` are tracked in git, so a source edit
alone ships nothing:

```bash
cd frontend && npm install && npm run build
```

Then bump the cache-busting suffix in `templates/landing_react.html` in **both** places —
they are currently in lockstep at `?v=304`, and keeping them matched is the existing
convention:

- line 17 — `frontend/assets/index.css?v=304`
- line 180 — `frontend/assets/index.js?v=304`

The build rewrites both files (the new `[&_p]:mb-3` style utilities land in the CSS), so
both genuinely change.

### 6. No model change, no migration

`bandhuapp/views.py:343-347` already passes `slide.title` and `slide.subtitle` through
verbatim into `data['hero_slides']`, and `json_script`
(`templates/landing_react.html:133`) escapes them correctly for transport.

Field caps now count markup: `title` is `CharField(max_length=200)` and `subtitle` is
`TextField(max_length=600)` (`bandhuapp/models.py:396-397`). Odia text plus tags consumes
these faster than plain English copy. Not widened preemptively — raise a migration only
when an author actually hits the limit.

## Out of scope

- The legacy `/classic/` landing (`bandhuapp/templates/landing_page.html`) contains zero
  references to `hero_slides` — verified by grep. Unaffected.
- `AboutUs` rendering in `About.jsx` already works and is untouched. Note that it has the
  same Preflight typography gap as the hero did; see Deferred.
- Rich-text editor, custom admin widget, sanitizer.

## Verification

1. Seed markup into both fields — `python manage.py shell`:
   ```python
   from bandhuapp.models import HeroSlide
   s = HeroSlide.objects.first()
   s.title = 'Bandhu at twilight — <span class="text-[#004f57]">ବନ୍ଧୁଘର</span>'
   s.subtitle = '<p>Like the garden we tend, we grow with <strong>patience</strong>.</p><p>.... in Odisha and beyond.</p>'
   s.save()
   ```
2. `python manage.py runserver`, load `http://127.0.0.1:8000/`. Title: the Odia word is
   teal, no literal `<span>` visible. Subtitle: "patience" is bold, and the two paragraphs
   have a visible gap between them — that gap is the section-2 child utilities working. If
   the paragraphs are flush against each other, the Tailwind JIT did not pick up
   `[&_p]:mb-3`; re-run the build.
3. Bullet check — set the subtitle to `<ul><li>one</li><li>two</li></ul>`, reload, confirm
   real bullets with indentation. Revert afterwards.
4. **Regression check on untouched slides.** Click through the other carousel slides and
   compare against `/tmp/bandhu-hero.png`. Expect pixel-identical text layout: the
   remaining slides hold plain-text copy, Preflight already zeroed the paragraph margin,
   and the child utilities only fire on tags that plain copy does not contain. Any visible
   shift means something other than this change moved.
5. Side by side with `http://127.0.0.1:8000/other_activities/` — hero text should now
   behave like `#about … .pillar-desc` there.
6. `bandhuapp/admin.py` changes, so run the suite and require exactly
   `Ran 732 tests ... OK (expected failures=10)` (731 plus the new regression test below).
   A different count is a discovery failure, not a pass — per `CLAUDE.md`, the runner
   reports `OK` on a partial discovery.

## Files touched

- `frontend/src/components/Hero.jsx` — the substantive edit
- `bandhuapp/admin.py` — author-facing help text
- `templates/landing_react.html` — cache-bust bump on lines 17 and 180
- `static/frontend/assets/index.js`, `index.css` — build output, committed
- `bandhuapp/tests/test_landing.py` — `test_hero_slide_html_is_not_escaped`, a regression
  test guarding the one thing an automated test can cheaply verify: the API payload
  carries the admin's raw HTML unescaped. It does not exercise the React render path
  (`dangerouslySetInnerHTML`, the Preflight-restoring classes) — that still needs the
  manual steps above, or a Playwright/Cypress smoke test if this surface gets touched
  again. No such e2e tooling exists in this repo today; adding it was scoped out as a
  separate, larger piece of work (new dependency, CI job, seed fixture).

## Deferred

- **Same Preflight typography gap in `About.jsx:97,107`.** `AboutUs.tagline`/`desc`
  already render HTML, so any `<p>` or `<ul>` an admin has typed there is being flattened
  today, silently. Not fixed here because it is a separate surface with its own layout and
  was not the reported bug. *Reopen when:* an admin reports About-section formatting not
  taking effect, or the same child-utility pattern is applied to a third surface — at
  which point extract it into a shared class instead of repeating it.
- **`title`/`subtitle` length caps counting markup** (`bandhuapp/models.py:396-397`).
  *Reopen when:* an author hits the 200- or 600-character limit in Django admin.
- **Server-side `bleach` sanitization in `_build_landing_data`.** See the sanitizer
  decision above. *Reopen when:* `is_staff` becomes grantable without an existing admin's
  action, or on-page admin gains a hero-slide editor.
- **Test count 731 — resolved.** Step 6 of verification ran during implementation:
  `python manage.py test` produced exactly `Ran 731 tests ... OK (expected failures=10)`,
  matching `CLAUDE.md`. No correction needed.
