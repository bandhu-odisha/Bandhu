import hashlib
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


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

