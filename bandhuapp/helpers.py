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


# Old live-site Core Team subtitles (org labels), not real occupations.
CORE_TEAM_LEGACY_SUBTITLES = frozenset({
    'upadestha',
    'upadeshta',
    'core team',
    'core team member',
    'sampadaka',
    'sampark pramukh',
})


def clean_core_team_profession_text(raw):
    if not raw:
        return ''
    text = raw.strip()
    text = re.sub(
        r'\s*\(\s*core\s+team(\s+member)?\s*\)\s*$',
        '',
        text,
        flags=re.I,
    ).strip()
    return text


def is_core_team_legacy_subtitle(text):
    cleaned = clean_core_team_profession_text(text)
    return cleaned.lower() in CORE_TEAM_LEGACY_SUBTITLES if cleaned else False


def core_team_card_lines(profile_profession, desc, staff_about=''):
    """
    Core Team cards: line 2 = org role (Upadestha, Sampadaka, …),
    line 3 = real profession. Role in desc; job in profile.profession or staff.about.
    """
    profile_p = clean_core_team_profession_text(profile_profession or '')
    desc_p = clean_core_team_profession_text(desc or '')
    about_p = clean_core_team_profession_text(staff_about or '')
    position = ''
    occupation = ''

    if is_core_team_legacy_subtitle(desc_p):
        position = desc_p
        if profile_p and not is_core_team_legacy_subtitle(profile_p):
            if profile_p.lower() != desc_p.lower():
                occupation = profile_p
    elif is_core_team_legacy_subtitle(profile_p):
        position = profile_p
        if desc_p and not is_core_team_legacy_subtitle(desc_p):
            if desc_p.lower() != profile_p.lower():
                occupation = desc_p
    elif desc_p and profile_p:
        if desc_p.lower() != profile_p.lower():
            position = desc_p
            occupation = profile_p
        else:
            occupation = profile_p
    elif desc_p:
        if is_core_team_legacy_subtitle(desc_p):
            position = desc_p
        else:
            occupation = desc_p
    elif profile_p:
        if is_core_team_legacy_subtitle(profile_p):
            position = profile_p
        else:
            occupation = profile_p

    if position and not occupation and about_p:
        if not is_core_team_legacy_subtitle(about_p):
            if about_p.lower() != position.lower():
                occupation = about_p

    lines = []
    if position:
        lines.append(proper_case(position))
    if occupation:
        occ = proper_case(occupation)
        if not lines or occ.lower() != lines[0].lower():
            lines.append(occ)
    return lines


def peoples_designation_dedupe_key(pd):
    """One row per staff+designation when role is empty (Core Team duplicates)."""
    if pd.role_id is None:
        return (pd.staff_id, pd.designation_id)
    return (pd.staff_id, pd.designation_id, pd.role_id)


def dedupe_peoples_designations(assignments):
    """
    Drop duplicate PeoplesDesignation rows.
    NULL role breaks SQL unique constraints, so Core Team rows dedupe by staff+designation.
    """
    best = {}
    for pd in assignments:
        key = peoples_designation_dedupe_key(pd)
        if key not in best:
            best[key] = pd
            continue
        current = best[key]
        if pd.rank < current.rank or (
            pd.rank == current.rank and pd.pk < current.pk
        ):
            best[key] = pd
    return sorted(
        best.values(),
        key=lambda pd: (pd.designation.rank, pd.rank, pd.pk),
    )


def remove_duplicate_peoples_designations():
    """Delete duplicate PeoplesDesignation rows from the database."""
    from django.db.models import Count, Min

    from bandhuapp.models import PeoplesDesignation

    removed = 0

    null_role_groups = (
        PeoplesDesignation.objects.filter(role__isnull=True)
        .values('staff_id', 'designation_id')
        .annotate(cnt=Count('id'), keep_pk=Min('id'))
        .filter(cnt__gt=1)
    )
    for group in null_role_groups:
        qs = PeoplesDesignation.objects.filter(
            staff_id=group['staff_id'],
            designation_id=group['designation_id'],
            role__isnull=True,
        ).exclude(pk=group['keep_pk'])
        removed += qs.count()
        qs.delete()

    duplicate_groups = (
        PeoplesDesignation.objects.filter(role__isnull=False)
        .values('staff_id', 'designation_id', 'role_id')
        .annotate(cnt=Count('id'), keep_pk=Min('id'))
        .filter(cnt__gt=1)
    )
    for group in duplicate_groups:
        qs = PeoplesDesignation.objects.filter(
            staff_id=group['staff_id'],
            designation_id=group['designation_id'],
            role_id=group['role_id'],
        ).exclude(pk=group['keep_pk'])
        removed += qs.count()
        qs.delete()

    for staff_id, designation_id in (
        PeoplesDesignation.objects.filter(role__isnull=False)
        .values_list('staff_id', 'designation_id')
        .distinct()
    ):
        orphans = PeoplesDesignation.objects.filter(
            staff_id=staff_id,
            designation_id=designation_id,
            role__isnull=True,
        )
        if orphans.exists():
            removed += orphans.count()
            orphans.delete()

    return removed


def _people_card_namespace(staff, position_line='', occupation_line='', groups_line=''):
    from types import SimpleNamespace

    return SimpleNamespace(
        staff=staff,
        position_line=proper_case(position_line) if position_line else '',
        occupation_line=proper_case(occupation_line) if occupation_line else '',
        groups_line=proper_case(groups_line) if groups_line else '',
    )


def _lines_to_position_occupation(lines):
    """Map display_lines to line 2 (position) and line 3 (occupation)."""
    cleaned = [ln for ln in lines if (ln or '').strip()]
    if len(cleaned) >= 2:
        return cleaned[0], cleaned[1]
    if len(cleaned) == 1:
        if is_core_team_legacy_subtitle(cleaned[0]):
            return cleaned[0], ''
        return '', cleaned[0]
    return '', ''


def people_card_from_assignments(assignments):
    """
    One people-page card from one or more PeoplesDesignation rows.
    When a person is on Core Team and Office Bearers, show them once on the
    All tab with their primary role plus a combined groups line.
    """
    assignments = list(assignments)
    staff = assignments[0].staff

    if len(assignments) == 1:
        pd = assignments[0]
        position_line, occupation_line = _lines_to_position_occupation(
            pd.display_lines
        )
        return _people_card_namespace(
            staff, position_line, occupation_line
        )

    office_roles = []
    group_names = []
    for pd in assignments:
        title = pd.designation.title
        if title not in group_names:
            group_names.append(title)
        if pd.role_id:
            office_roles.append(pd.role.title)

    position_line = ''
    occupation_line = ''
    groups_line = ''

    if office_roles:
        position_line = ' \u00b7 '.join(proper_case(r) for r in office_roles)
    else:
        for pd in assignments:
            card_lines = pd.display_lines
            if card_lines and card_lines[0]:
                position_line = card_lines[0]
                break

    if len(group_names) > 1:
        groups_line = ' \u00b7 '.join(group_names)
    elif len(assignments) > 1:
        groups_line = ' \u00b7 '.join(
            pd.role.title if pd.role_id else pd.designation.title
            for pd in assignments
        )

    shown_position = {position_line} if position_line else set()
    shown_occupation = set()

    for pd in assignments:
        if pd.designation.title == 'Core Team' and not pd.role_id:
            ct_pos, ct_occ = _lines_to_position_occupation(
                core_team_card_lines(
                    pd.staff.profile.profession if pd.staff_id else '',
                    pd.desc,
                    pd.staff.about if pd.staff_id else '',
                )
            )
            if ct_pos and ct_pos not in shown_position:
                position_line = ct_pos
                shown_position.add(ct_pos)
            if ct_occ and ct_occ not in shown_occupation:
                occupation_line = ct_occ
                shown_occupation.add(ct_occ)
            continue
        occ = (pd.desc or '').strip()
        if not occ and pd.staff_id:
            occ = (pd.staff.profile.profession or '').strip()
        occ = proper_case(occ)
        if occ and occ not in shown_occupation and occ not in shown_position:
            occupation_line = occ
            break

    return _people_card_namespace(
        staff, position_line, occupation_line, groups_line
    )

