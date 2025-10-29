import os
import re
import sqlite3

# --- CONFIG ---
media_dir = r"C:\Users\niran\AppData\Roaming\Anki2\User 1\collection.media"
db_path = r"C:\Users\niran\AppData\Roaming\Anki2\User 1\collection.anki2"
deck_name = "Core_2k_6k_Japanese_Deck"

# --- DB setup ---
def unicase_collation(s1, s2):
    return (s1.casefold() > s2.casefold()) - (s1.casefold() < s2.casefold())

conn = sqlite3.connect(db_path)
conn.create_collation("unicase", unicase_collation)
cursor = conn.cursor()

# --- Step 1: cards with images ---
query = """
SELECT n.id, n.flds
FROM notes n
JOIN cards c ON n.id = c.nid
WHERE c.did = (SELECT id FROM decks WHERE name = ? COLLATE unicase);
"""
cursor.execute(query, (deck_name,))
notes = cursor.fetchall()

cards_with_images = []
image_names_in_cards = set()

for note_id, fields in notes:
    imgs = re.findall(r'<img src="([^"]+)"', fields)
    if imgs:
        cards_with_images.append(note_id)
        for img in imgs:
            image_names_in_cards.add(img)

print(f"1 Cards with images: {len(cards_with_images)}")

# --- Step 2: image files in media folder ---
all_media_files = os.listdir(media_dir)
resized_images = [f for f in all_media_files if f.startswith("resized_")]
print(f"2 Media files with 'resized_' prefix: {len(resized_images)}")

# --- Step 3: compare card references vs resized images ---
resized_in_cards = [i for i in image_names_in_cards if i.startswith("resized_")]
non_resized_in_cards = [i for i in image_names_in_cards if not i.startswith("resized_")]

print(f"3 Cards using 'resized_' images: {len(resized_in_cards)}")
print(f"   Cards using NON-resized images: {len(non_resized_in_cards)}")

# --- Step 4: potential fix candidates ---
fix_candidates = []
for img in non_resized_in_cards:
    if os.path.exists(os.path.join(media_dir, f"resized_{img}")):
        fix_candidates.append(img)

print(f"4 Images that can be safely fixed by prefixing: {len(fix_candidates)}")

conn.close()
