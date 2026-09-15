# Show an honest visitor count on the public home page

## Objective

Display `HomePage.visitors_count` on the public home page, counting only real
browser visits — not the bots, monitors and crawlers the current mechanism also
counts.

**Outcome ledger:** the metric is `visitors_count` itself
(`bandhuapp/models.py:415`), written by the new `visit_beacon` view. Success is
observed by comparing its growth rate against `django_session` row growth before
vs. after deploy — bot-driven inflation shows as counter growth with no matching
session growth today, and should disappear after. No new logging artifact is
added; the existing field is the record.

## Problem

The counter has existed since 2020-09-23 (commit `276d87d`). Two defects, both
confirmed against current code:

**1. Invisible.** The only display is `templates/snippets/footer.html:41-42`,
gated on `user.is_admin`. `content` is passed only by three views
(`bandhuapp/views.py:182`, `:605`, `:670`) via a template context dict, not a
context processor — most pages never receive it. `_build_landing_data`
(`bandhuapp/views.py:191`) does not serialize `visitors_count` at all, so the
React home page — `templates/landing_react.html`, served by `index_react`
(`bandhuapp/views.py:506`) — cannot show it under any user.

**2. Counts bots.** Both increment sites gate on a session flag:

```python
if not request.session.get('home_page_visited', False):
    request.session['home_page_visited'] = True
    HomePage.objects.all().update(visitors_count=F('visitors_count') + 1)
```

(`bandhuapp/views.py:156-159` classic `index`; `:511-513` React `index_react`,
identical.) A client that does not persist cookies gets a fresh, empty session
on every request, so `request.session.get(...)` returns `False` every time and
the counter increments on every hit — unbounded. `find . -name robots.txt`
across the repo returns nothing, so nothing discourages crawler traffic. Each
such hit also writes a `django_session` row (`django.contrib.sessions` is
installed, `bandhu/settings.py:43`), so the table grows with every bot request.

Because there is no timestamp or IP stored — `visitors_count` is a single
`IntegerField`, `bandhuapp/models.py:415` — the current total cannot be
retroactively split into human vs. bot. It is presented, kept, and not reset (see
Decisions).

## Not a blocker: the audit's caching claim

`DONE/planning/2026-09-12-cx-audit/report.md:16` (finding W01) states the
session write "makes Cloudflare unable to cache the page." Checked and
contradicted for this code path: `index_react` also calls
`_must_complete_member_profile(request.user)` (`bandhuapp/views.py:508`), which
evaluates `user.is_authenticated` and touches the session, and
`get_token(request)` (`:523`), which issues a CSRF cookie — both force
`Vary: Cookie` independently of the visitor counter. Removing the counter's
session write would not restore cacheability on its own; that is separate,
undone work (commit `58ec6ac`, the prior load-time fix, never touched
`home_page_visited` — confirmed, `git show 58ec6ac -- bandhuapp/views.py | grep
home_page_visited` returns nothing).

What this change *does* fix: moving the count off the request path means no
`django_session` row is created for an anonymous visit at all (see Decisions).
That's W01's row-growth half, closed as a side effect.

No caching exists on `_build_landing_data` or `index_react`
(`grep -E "cache" bandhuapp/views.py` returns nothing), so any displayed count
is fresh per request — not a factor in the design.

## Decisions

Resolved live via `grill-me` in this session; labelled `PROVIDED` — each is a
judgment call the evidence alone could not settle, not a checkable code fact, so
none is re-verified against a citation.

- **PROVIDED — count via a JS beacon, not the server-rendered request.** A
  `fetch` fired after the React app mounts only runs in a real browser. Bots,
  monitors, and `curl` never execute it, so they stop counting entirely. This is
  the fix for defect 2.
- **PROVIDED — dedupe with `localStorage`, not a server session.** The beacon
  view stays stateless: no session read, no session write, so anonymous visits
  create zero `django_session` rows (closing W01's row-growth half). Trade-off
  accepted: a private window or cleared browser storage will beacon again, same
  failure mode the current session cookie already has.
  A named alternative — gating on `request.session.session_key is not None` —
  was considered and rejected: it undercounts genuine first-time visitors, who
  are cookieless on their very first request by definition.
- **PROVIDED — footer line, not a stat strip or milestone badge.** Production
  count sits in the 2,000–50,000 range: real, but not a headline number.
- **PROVIDED — wording is `"N visits"`, not `"visitors"` or `"...since 2020"`.**
  "Visitors" overclaims: the mechanism counts browsers (one person on phone +
  laptop = two), so "visits" is the accurate noun. A "since" date was
  considered and rejected — `visitors_count` is a freely-editable admin field
  (`bandhuapp/admin.py:263`, no read-only constraint), so no anchor date is
  provable even though `276d87d` dates the field's origin.
- **PROVIDED — classic footer gets the same wording and loses its admin gate.**
  Keeps one fact presented one way, rather than "Visitors Count: N" to admins
  and "N visits" to everyone else on the same field.
- **PROVIDED — the existing total is kept, not reset to zero.** The six years of
  bot-polluted history ships as-is under the new, accurate label. Explicit
  user decision, made after being told the total's provenance is unverifiable.

## Design

### 1. Beacon endpoint

New view, `bandhuapp/views.py`, beside `landing_api` (`:497-503`):

```python
@require_POST
def visit_beacon(request):
    """Count one real-browser visit to the home page."""
    HomePage.objects.all().update(visitors_count=F('visitors_count') + 1)
    return JsonResponse({'ok': True})
```

`F` and `HomePage` are already imported in this module (used identically at
`:159`/`:513`). Route in `bandhuapp/urls.py`, beside `api/landing/` (`:8`):

```python
path('api/visit/', views.visit_beacon, name="visit_beacon"),
```

Django's default CSRF protection applies; the token is already shipped in
`landing_data['csrf_token']` (`bandhuapp/views.py:523`). No session access in
this view — satisfies the stateless decision above.

### 2. Remove both server-side increments

Delete `bandhuapp/views.py:156-159` (classic `index`) and `:511-513` (React
`index_react`). `/classic/` has no React and therefore stops counting
entirely — a legacy page (`templates/landing_react.html` is what
`index_react` serves; `index` backs `/classic/` per `bandhuapp/urls.py`) losing
a bot-inflated count is a net improvement, not a regression.

### 3. Fire the beacon from React

`frontend/src/App.jsx`, new effect after the existing hash-scroll effect
(after line 99, `}, [data])`):

```jsx
useEffect(() => {
  if (!data) return
  try {
    if (localStorage.getItem('bandhu_visited')) return
    localStorage.setItem('bandhu_visited', '1')
  } catch {
    return
  }
  fetch('/api/visit/', {
    method: 'POST',
    headers: { 'X-CSRFToken': data.csrf_token || '' },
  }).catch(() => {})
}, [data])
```

The `try/catch` around `localStorage` access matters — Safari private windows
and locked-down storage settings can throw on read/write, and a thrown error
here must not break page render. The `fetch(...).catch(() => {})` makes the
beacon fire-and-forget: a failed POST must never surface to the visitor. A
first-time visitor's own beacon lands after the page's initial server render,
so their footer count is one behind their own visit — acceptable; not worth a
second round-trip to correct.

### 4. Serialize the count to the frontend

`bandhuapp/views.py:342`, inside the existing `if content:` block that already
builds `data['content']`:

```python
data['content'] = {
    'banner_image': banner_url,
    'banner_image_responsive': banner_responsive,
    'visitors_count': content.visitors_count,
}
```

`content` in this scope is `HomePage.objects.all().first()`
(confirmed context: `_build_landing_data`'s local `content` variable, set
earlier in the function from the same query pattern used at `:182`/`:605`/`:670`).
This dict already crosses to React via `landing_data|json_script` and to
`landing_api` (`:498-503`, read-only, no increment) for free.

### 5. React footer line

`frontend/src/components/Footer.jsx`, inside the existing
`border-t border-white/20` block (line ~191), above the `©` paragraph:

```jsx
{data?.content?.visitors_count > 0 && (
  <p className="mb-2 text-white/70">
    {data.content.visitors_count.toLocaleString('en-IN')} visits
  </p>
)}
```

`> 0` mirrors the classic template's existing truthiness guard
(`{% if content and content.visitors_count %}`) — a fresh install with `0`
renders nothing rather than "0 visits". `en-IN` grouping matches the site's
audience. `text-white/70` sits one shade below the copyright's
`text-white/90` so it reads as a footnote, not a headline.

### 6. Classic footer

`templates/snippets/footer.html:41-42`:

```django
{% if content and content.visitors_count %}
<p class="contact-footer-visitors mt-3 mb-0">{{ content.visitors_count|intcomma }} visits</p>
{% endif %}
```

Requires `{% load humanize %}` at the top of this template, and
`'django.contrib.humanize'` added to `INSTALLED_APPS`
(`bandhu/settings.py:39-60`) — **confirmed absent**, `grep -n humanize
bandhu/settings.py` returns nothing before this change. Ships with Django;
no new dependency. `.contact-footer-visitors` CSS (`css/custom.css:885-888`)
is reused unchanged.

### 7. Tests

Both existing counter tests assert the behavior this change removes and must be
rewritten, not just left passing by accident:

- `bandhuapp/tests/test_landing.py:112-117`
  (`test_visitor_count_increments_once_per_session`)
- `bandhuapp/tests/test_views_coverage.py:57-62` (same assertion shape)

New assertions, replacing the old body in both files:
- `GET /` does not change `visitors_count` — this is the regression guard for
  defect 2 and the one that matters most.
- `POST /api/visit/` increments by exactly 1.
- `landing_data['content']['visitors_count']` carries the current value
  (extends `test_views_coverage.py:519`
  `test_about_and_volunteer_and_content_present`, which already builds a
  `HomePage` with `visitors_count=0`).

Test count changes from 736; update `CLAUDE.md`'s hardcoded figure to match
whatever `python manage.py test` reports after these edits — do not guess the
new number in advance.

### 8. Build and cache-bust

```bash
cd frontend && npm install && npm run build
```

Bump `?v=307` → `?v=308` on both `templates/landing_react.html:27`
(`index.css`) and `:190` (`index.js`) — confirmed current value at both
locations. Commit `static/frontend/assets/` output per repo convention
(`CLAUDE.md`: "build output is COMMITTED").

## Completeness sweep

| Reference | Status | Note |
|---|---|---|
| `HomePage.visitors_count` | Specified | `bandhuapp/models.py:415`, existing field, no schema change |
| `bandhuapp/urls.py` route table | Specified | new line added beside confirmed existing `api/landing/` entry |
| `data['content']` dict shape | Specified | existing dict, one key added, confirmed producer at `:342` |
| `django.contrib.humanize` | **Nonexistent → added** | confirmed absent from `INSTALLED_APPS`; this spec adds it (step 6) — not a blocker, stdlib-shipped |
| `localStorage['bandhu_visited']` | Specified | new key, single writer (`App.jsx` effect), single reader (same effect) |
| `/api/visit/` CSRF token source | Specified | reuses existing `data.csrf_token`, confirmed producer `bandhuapp/views.py:523` |
| `django_session` table | Referenced-only, not modified | cited as the cost this change removes; no schema or admin change to it |
| `robots.txt` | Nonexistent | confirmed absent repo-wide; explicitly out of scope, not a dependency of this design (beacon approach doesn't need it) |

No blockers. Every field and file this design writes to or reads from is either
already producing what the design needs, or is added by this spec.

## Verification

```bash
source venv/bin/activate
python manage.py test 2>err.log >/dev/null; tail -20 err.log
```

Expect `OK (expected failures=10)`, test count matching the updated `CLAUDE.md`
figure. Any other count is a discovery failure, not a pass
(`CLAUDE.md`: "treat any count other than [documented number] as a broken
build until explained").

End-to-end:

```bash
python manage.py runserver
```

1. `/admin/bandhuapp/homepage/` — note current `visitors_count`.
2. `curl -s localhost:8000/ > /dev/null` — count unchanged. **This is the
   defect-2 regression check; if this fails, the fix did nothing.**
3. Open `/` in a fresh private window → footer shows the formatted count above
   the copyright; refresh admin page → count is +1.
4. Reload the same window → count unchanged (localStorage dedup holds).
5. New private window → +1 again.
6. `/classic/`, logged out → same wording appears in the classic footer.
7. `curl -s localhost:8000/api/landing/ | python -m json.tool | grep
   visitors_count` → value present, unchanged by the curl itself.
8. Set `visitors_count` to `0` in admin → both footers render no line.

## Deferred

- **`robots.txt`** — worth adding for general crawler hygiene, but not a
  dependency of this design (the beacon approach makes the counter bot-proof
  without it). Reopen when: human call — decide whether crawler noise in
  server logs/analytics elsewhere warrants it, independent of this feature.
- **Rate-limiting `/api/visit/`** — a determined actor could script repeated
  POSTs to inflate a vanity counter. Reopen when: `visitors_count` growth rate
  is observed exceeding plausible organic traffic after deploy (see Outcome
  ledger comparison).
- **Splitting the historical total into human vs. bot** — NO EVIDENCE. Checked
  and confirmed impossible: `visitors_count` is a bare `IntegerField` with no
  timestamp or IP ever stored (`bandhuapp/models.py:415`), so there is no data
  to retroactively filter. Reopen when: never, unless a decision is later made
  to reset the counter and start clean (see Decisions — explicitly rejected for
  this change).
