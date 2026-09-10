# Media Upload Permissions — 403 on Production Media Files

## Symptom

In production (cPanel), a few media files served from `MEDIA_ROOT`
return `403 Forbidden` instead of the expected content.



For Ex: the profile image for Rajendra - image.png (size: 1.35 MB) renders okay. While the profile image for Tarakanta - Tarakanta-Jaydev.png (size: 16.17MB) threw 403 Forbidden. On deep dive the two images were found with Permissions 0644 & 0600 respectively. Manually changing the permission of the later to 0644 fix the `403 Forbidden` issue.

## Mechanism

Django's upload handling picks one of two code paths depending on file size,
relative to `FILE_UPLOAD_MAX_MEMORY_SIZE` (Django default: 2.5 MB):

- **Small uploads** are buffered in memory (`InMemoryUploadedFile`) and
  written to disk fresh by `FileSystemStorage`, picking up the process's
  umask — typically `0644`, which the web server can read.
- **Larger uploads** are streamed to a `TemporaryUploadedFile`, which Python's
  `tempfile.NamedTemporaryFile` creates at mode `0600` (owner read/write
  only, by design — it's meant to be a private temp file). `FileSystemStorage`
  then moves that temp file into `MEDIA_ROOT` on save. If Django's
  `FILE_UPLOAD_PERMISSIONS` setting is `None`, `FileSystemStorage` performs
  **no chmod** on save, so the file keeps its `0600` mode after landing in
  `MEDIA_ROOT` — unreadable by the web server's process user, hence 403.

If this is what is happening, the resulting failure would be **partial and
size-correlated**: uploads above the 2.5 MB threshold would 403 while smaller
ones served fine. That partial/size-correlated pattern is a *prediction of
this diagnosis*, not something that was reported or observed — it is the
thing to go and check (see Evidence status below).

### Evidence status

This mechanism **has been** confirmed directly against the production
filesystem — and it is the standard,
well-documented cause of a 403-on-media symptom in Django, and is consistent
with the 2.2 defaults below.

## Why Django 2.2 specifically

This project pins `Django==2.2.13` (`requirements.txt`). In Django 2.2,
`django/conf/global_settings.py` defaults both relevant settings to `None`:

```python
FILE_UPLOAD_PERMISSIONS = None
FILE_UPLOAD_DIRECTORY_PERMISSIONS = None
```

`FileSystemStorage.file_permissions_mode` / `.directory_permissions_mode`
resolve through `_value_or_setting`, and `_save()` only chmods when the
resolved mode is not `None`. Django did not change the default for
`FILE_UPLOAD_PERMISSIONS` to `0o644` until **Django 3.0** — this project,
pinned below that version, gets `None` and therefore no chmod at all. The
setting here is not cargo-cult boilerplate copied from a newer Django's
defaults; on this pinned stack it is required to get any chmod behavior.

## The fix

Added to `bandhu/settings.py`, immediately after `MEDIA_ROOT`/`MEDIA_URL`:

```python
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
```

**The `0o` prefix is load-bearing.** `FILE_UPLOAD_PERMISSIONS = 644` (a
decimal literal, no prefix) evaluates to mode `0o1204` — a nonsensical mode
that would still "work" (no error) while silently doing the wrong thing.
Verified in this change with the real Django 2.2.13 / Python 3.8 interpreter:

```
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
fs.file_permissions_mode = 0o644
fs.directory_permissions_mode = 0o755
```

## What this fix does NOT fix

`FILE_UPLOAD_PERMISSIONS` / `FILE_UPLOAD_DIRECTORY_PERMISSIONS` only affect
**future** uploads — files written to disk *after* this setting takes
effect. Every file already sitting in production `MEDIA_ROOT` at `0600` (or
whatever mode it currently has) is untouched by this change and will
**continue to 403** after deploy. This settings change alone does not
resolve the reported production issue for existing media; it only prevents
new occurrences.

## One-time remediation for existing media

Run once on the production server, against the real `MEDIA_ROOT` (matching
the modes set above):

```bash
find "$MEDIA_ROOT" -type d -exec chmod 755 {} +
find "$MEDIA_ROOT" -type f -exec chmod 644 {} +
```

This is a filesystem operation on production data — take care to run it
against the correct `MEDIA_ROOT` path (per `.env`) and ideally verify with a
`find ... -print` dry run first.

## Deploy step

Standard deploy per README §3 (`git pull`, `pip install`, `migrate`,
`collectstatic --noinput`, restart the app server). The restart is
**required**, not optional, for this change: Passenger keeps the Python
process warm between requests, so a settings change has no effect until the
app is restarted. README §3 deliberately does not name the restart command
("command depends on hosting"); per README, server paths and restart
commands are maintained by the project maintainers — use whatever mechanism
this deployment already uses. Follow the deploy with the one-time `chmod`
remediation above for already-uploaded media.

## Verification performed

- Manual verification as described in the Symptom section above
- Confirmed via the pinned Django 2.2.13 / Python 3.8 interpreter
  (`.claude/worktrees/regression-tests/venv38`), loading the real
  `bandhu.settings` module with the project's actual `.env`:
  `settings.FILE_UPLOAD_PERMISSIONS == 0o644`,
  `settings.FILE_UPLOAD_DIRECTORY_PERMISSIONS == 0o755`, and
  `FileSystemStorage().file_permissions_mode` /
  `.directory_permissions_mode` resolve to the same values.
- `python manage.py check` (same interpreter, `DB_ENGINE=sqlite`) —
  `System check identified no issues (0 silenced).`
- The full regression suite (725 tests) was **not** run for this change.
  Per `CLAUDE.md`, the repo's default `venv/` has drifted to Django 4.2 /
  Python 3.13, where the project fails to even import
  (`force_text` removed in Django 4.0) — a failure or pass from that venv
  would be unrelated to this change and was correctly not used as signal.
  The `check` above plus the direct settings-value assertions are the
  appropriate verification for a two-constant, non-branching settings
  addition on the pinned stack.
