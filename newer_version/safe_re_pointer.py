"""
anki_fix_resized.py
Adds 'resized_' prefix to <img src="..."> entries in notes when the corresponding
file 'resized_<name>' exists in the Anki media folder.

- Makes a timestamped backup of collection.anki2 before modifying.
- Writes a CSV report of changes.

Edit the three CONFIG values below if your paths/deck-name differ.
"""

import os
import re
import sqlite3
import shutil
import csv
from datetime import datetime

# ---------- CONFIG (edit if needed) ----------
MEDIA_DIR = r"C:\Users\niran\AppData\Roaming\Anki2\User 1\collection.media"
DB_PATH = r"C:\Users\niran\AppData\Roaming\Anki2\User 1\collection.anki2"
DECK_NAME = "Core_2k_6k_Japanese_Deck"
# ----------------------------------------------

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_PATH = DB_PATH + f".backup_{TIMESTAMP}"
REPORT_CSV = f"fix_report_{TIMESTAMP}.csv"

# helper: unicase collation as you used before
def unicase_collation(s1, s2):
    return (s1.casefold() > s2.casefold()) - (s1.casefold() < s2.casefold())

def make_backup():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"DB not found at {DB_PATH}")
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"[backup] Created DB backup: {BACKUP_PATH}")

def gather_notes(cursor):
    query = """
    SELECT n.id, n.flds
    FROM notes n
    JOIN cards c ON n.id = c.nid
    WHERE c.did = (SELECT id FROM decks WHERE name = ? COLLATE unicase);
    """
    cursor.execute(query, (DECK_NAME,))
    return cursor.fetchall()

def find_img_srcs(fields):
    # find src values inside <img ... src="..."> occurrences
    return re.findall(r'<img[^>]*\s+src="([^"]+)"', fields)

def update_notes():
    conn = sqlite3.connect(DB_PATH)
    conn.create_collation("unicase", unicase_collation)
    cur = conn.cursor()

    notes = gather_notes(cur)
    total_notes = len(notes)
    print(f"[scan] Total notes in deck '{DECK_NAME}': {total_notes}")

    updated_count = 0
    replaced_entries = []  # list of tuples for CSV: (note_id, original_src, replaced_src, status)

    for note_id, fields in notes:
        img_srcs = find_img_srcs(fields)
        if not img_srcs:
            continue

        original_fields = fields
        new_fields = fields
        any_change = False

        # for each src that doesn't already start with resized_, check for resized_ file
        for src in img_srcs:
            if src.startswith("resized_"):
                # already prefixed - skip
                replaced_entries.append((note_id, src, src, "already_prefixed"))
                continue

            candidate = f"resized_{src}"
            candidate_path = os.path.join(MEDIA_DIR, candidate)

            if os.path.exists(candidate_path):
                # Replace ONLY the exact src occurrence(s)
                # Use a safe replace that targets src="...": avoids accidental substring hits
                # Pattern: src="old" -> src="resized_old"
                new_fields = new_fields.replace(f'<img src="{src}"', f'<img src="{candidate}"')
                any_change = True
                replaced_entries.append((note_id, src, candidate, "replaced"))
            else:
                replaced_entries.append((note_id, src, candidate, "no_resized_file"))

        if any_change and new_fields != original_fields:
            # write back to DB
            cur.execute("UPDATE notes SET flds = ? WHERE id = ?", (new_fields, note_id))
            updated_count += 1

    conn.commit()
    conn.close()
    return updated_count, replaced_entries

def write_csv_report(rows):
    header = ["note_id", "original_src", "replaced_src", "status"]
    with open(REPORT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"[report] CSV report written: {REPORT_CSV}")

def main():
    print("=== anki_fix_resized.py ===")
    print(f"DB: {DB_PATH}")
    print(f"Media dir: {MEDIA_DIR}")
    print(f"Deck: {DECK_NAME}")
    print("Creating backup...")

    make_backup()

    print("Applying updates (will only replace if 'resized_<src>' exists in media folder)...")
    updated_count, rows = update_notes()
    print(f"[done] Notes updated (notes with any change): {updated_count}")

    # summarise statuses
    from collections import Counter
    status_counter = Counter(r[3] for r in rows)
    print("[summary] statuses:")
    for k, v in status_counter.items():
        print(f"  {k}: {v}")

    write_csv_report(rows)

    # print a few sample replacements
    samples = [r for r in rows if r[3] == "replaced"][:50]
    if samples:
        print("\nSample replacements (up to 50):")
        for note_id, orig, repl, status in samples:
            print(f"  note {note_id}: {orig} -> {repl}")

    print("\nAll done. If anything looks wrong, restore the DB from the backup file:")
    print(f"  restore by copying {BACKUP_PATH} -> {DB_PATH} (while Anki is closed).")

if __name__ == "__main__":
    main()
