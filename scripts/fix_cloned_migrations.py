import os
import re

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'applications')
APPS = ['prasantaraktadan', 'patriotism', 'sevavrata']

RELATED = {
    'prasantaraktadan': 'prasantaraktadan_attendees',
    'patriotism': 'patriotism_attendees',
    'sevavrata': 'sevavrata_attendees',
}

for label in APPS:
    path = os.path.join(BASE, label, 'migrations', '0001_initial.py')
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Wrong FK field names from over-eager replace: use ashram like the source app.
    text = re.sub(
        rf"\('{label}', models\.ForeignKey",
        "('ashram', models.ForeignKey",
        text,
    )
    text = text.replace(
        "to='bandhuapp.Profile')",
        f"to='bandhuapp.Profile', related_name='{RELATED[label]}')",
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Fixed migration', label)
