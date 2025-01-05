import sqlite3
import re

db_path = "./collection.anki2"

# Define a custom collation function to mimic "unicase"
def unicase_collation(s1, s2):
    return (s1.casefold() > s2.casefold()) - (s1.casefold() < s2.casefold())

conn = sqlite3.connect(db_path)
# Register the custom collation
conn.create_collation("unicase", unicase_collation)

cursor = conn.cursor()

deck_name = "Core_2k_6k_Japanese_Deck"

# Function to update the back template with the resized prefix
def update_image_src():
    # Query to fetch the card ID and the back template from the specified deck
    query = """
    SELECT c.id, c.did, n.flds
    FROM cards c
    JOIN notes n ON c.nid = n.id
    WHERE c.did = (SELECT id FROM decks WHERE name = ? COLLATE unicase);
    """

    cursor.execute(query, (deck_name,))
    cards = cursor.fetchall()

    updated_count = 0

    # Loop through each card and update the `src` attribute
    for card_id, deck_id, fields in cards:
        # Use regex to find and replace the src attribute
        updated_fields = re.sub(
            r'<img src="(?!resized_)([^"]+)"',
            r'<img src="resized_\1"',
            fields
        )

        if updated_fields != fields:
            # Update the fields back into the database
            update_query = "UPDATE notes SET flds = ? WHERE id = (SELECT nid FROM cards WHERE id = ?);"
            cursor.execute(update_query, (updated_fields, card_id))
            updated_count += 1

    # Commit the changes
    conn.commit()
    return updated_count


# Execute the function
updated_count = update_image_src()

# Output the result
print(f"Updated {updated_count} cards with resized image prefixes.")

# Close the connection
conn.close()

echo "# God_Teir_Programming_in_Anki" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Niranjan-GopaL/God_Teir_Programming_in_Anki.git
git push -u origin main