"""Apply bandhuapp 0018_staff_qualifications_text without loading full Django."""
import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "db.sqlite3"
MIGRATION = "0018_staff_qualifications_text"


def year_from_date(value):
    if not value:
        return None
    return str(value)[:4]


def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    applied = cur.execute(
        "SELECT 1 FROM django_migrations WHERE app = ? AND name = ?",
        ("bandhuapp", MIGRATION),
    ).fetchone()
    if applied:
        print(f"{MIGRATION} already applied.")
        return

    cols = [r[1] for r in cur.execute("PRAGMA table_info(bandhuapp_staff)")]
    if "qualifications" not in cols:
        cur.execute(
            "ALTER TABLE bandhuapp_staff "
            "ADD COLUMN qualifications TEXT NOT NULL DEFAULT ''"
        )
        print("Added bandhuapp_staff.qualifications column.")

    table_exists = cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='bandhuapp_staffqualification'"
    ).fetchone()
    if table_exists:
        rows = cur.execute(
            """
            SELECT staff_id, degree, institute, since, until
            FROM bandhuapp_staffqualification
            ORDER BY staff_id, since, id
            """
        ).fetchall()
        by_staff = defaultdict(list)
        for row in rows:
            since_y = year_from_date(row["since"])
            line = f"{row['degree']}, {row['institute']} ({since_y}"
            until_y = year_from_date(row["until"])
            line += f" – {until_y}" if until_y else " – present"
            line += ")"
            by_staff[row["staff_id"]].append(line)

        for staff_id, lines in by_staff.items():
            text = "\n".join(lines)
            existing = cur.execute(
                "SELECT qualifications FROM bandhuapp_staff WHERE id = ?",
                (staff_id,),
            ).fetchone()
            if existing and (existing[0] or "").strip():
                continue
            cur.execute(
                "UPDATE bandhuapp_staff SET qualifications = ? WHERE id = ?",
                (text, staff_id),
            )
        cur.execute("DROP TABLE bandhuapp_staffqualification")
        print("Migrated and dropped bandhuapp_staffqualification.")

    cur.execute(
        "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, ?)",
        ("bandhuapp", MIGRATION, datetime.now().isoformat(sep=" ", timespec="seconds")),
    )
    conn.commit()
    conn.close()
    print(f"Recorded {MIGRATION} in django_migrations.")


if __name__ == "__main__":
    main()
