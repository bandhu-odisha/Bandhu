import hashlib
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


def proper_case(value):
    """Capitalise the first letter of each word; lowercase the rest."""
    if value is None:
        return value
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return text

    def _format_word(word):
        if not word:
            return word
        leading, core, trailing = '', word, ''
        while core and not core[0].isalnum():
            leading += core[0]
            core = core[1:]
        while core and not core[-1].isalnum():
            trailing = core[-1] + trailing
            core = core[:-1]
        if not core:
            return word
        return f'{leading}{core[:1].upper()}{core[1:].lower()}{trailing}'

    return ' '.join(_format_word(part) for part in text.split())


def _createHash():
    hash = hashlib.sha1()
    hash.update(str(time.time()).encode('utf-8'))
    return hash.hexdigest()[0:20]


def _format_duration_hms(seconds):
    s = max(0, int(seconds))
    h, mm, sec = s // 3600, (s % 3600) // 60, s % 60
    if h:
        return f'{h}:{mm:02d}:{sec:02d}'
    return f'{mm}:{sec:02d}'


def fetch_youtube_duration_formatted(video_id):
    """
    Read length from the public watch page (no API key).
    Used when Video.duration is blank in the admin.
    """
    if not video_id or not isinstance(video_id, str) or len(video_id) != 11:
        return None
    safe_id = urllib.parse.quote(video_id, safe='-_')
    url = f'https://www.youtube.com/watch?v={safe_id}'
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception:
        return None
    m = re.search(r'"lengthSeconds":"(\d+)"', html)
    if not m:
        m = re.search(r'"lengthSeconds":(\d+)', html)
    if m:
        return _format_duration_hms(int(m.group(1)))
    m = re.search(r'"approxDurationMs":"(\d+)"', html)
    if not m:
        m = re.search(r'"approxDurationMs":(\d+)', html)
    if m:
        return _format_duration_hms(int(m.group(1)) // 1000)
    return None


def enrich_video_durations(video_items, max_workers=4):
    """Set ``duration`` on items that have ``video_id`` but no duration yet."""
    need = [it for it in video_items if it.get('video_id') and not it.get('duration')]
    if not need:
        return
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        future_map = {
            ex.submit(fetch_youtube_duration_formatted, it['video_id']): it for it in need
        }
        for fut in as_completed(future_map):
            item = future_map[fut]
            try:
                d = fut.result()
                if d:
                    item['duration'] = d
            except Exception:
                pass


def people_card_from_assignments(assignments):
    """
    One people-page card from one or more PeoplesDesignation rows.
    When a person is on Core Team and Office Bearers, show them once on the
    All tab with their primary role plus a combined groups line.
    """
    from types import SimpleNamespace

    assignments = list(assignments)
    staff = assignments[0].staff

    if len(assignments) == 1:
        entries = []
        for index, text in enumerate(assignments[0].display_lines):
            kind = "position" if index == 0 else "occupation"
            entries.append({"text": proper_case(text), "kind": kind})
        return SimpleNamespace(staff=staff, display_entries=entries)

    office_roles = []
    group_names = []
    for pd in assignments:
        title = pd.designation.title
        if title not in group_names:
            group_names.append(title)
        if pd.role_id:
            office_roles.append(pd.role.title)

    entries = []
    if office_roles:
        entries.append(
            {
                "text": " \u00b7 ".join(proper_case(r) for r in office_roles),
                "kind": "position",
            }
        )
    else:
        for pd in assignments:
            card_lines = pd.display_lines
            if card_lines and card_lines[0]:
                entries.append({"text": card_lines[0], "kind": "position"})
                break

    if len(group_names) > 1:
        entries.append(
            {"text": " \u00b7 ".join(group_names), "kind": "groups"}
        )
    elif len(assignments) > 1:
        entries.append(
            {
                "text": " \u00b7 ".join(
                    pd.role.title if pd.role_id else pd.designation.title
                    for pd in assignments
                ),
                "kind": "groups",
            }
        )

    shown = {entry["text"] for entry in entries}
    for pd in assignments:
        occupation = (pd.desc or "").strip()
        if not occupation and pd.staff_id:
            occupation = (pd.staff.profile.profession or "").strip()
        occupation = proper_case(occupation)
        if occupation and occupation not in shown:
            entries.append({"text": occupation, "kind": "occupation"})
            break

    if not entries:
        entries = [{"text": "", "kind": "position"}]

    return SimpleNamespace(staff=staff, display_entries=entries)

