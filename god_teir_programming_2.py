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
    SELECT c.id, c.did, n.flds, n.id as note_id
    FROM cards c
    JOIN notes n ON c.nid = n.id
    WHERE c.did = (SELECT id FROM decks WHERE name = ? COLLATE unicase);
    """
    cursor.execute(query, (deck_name,))
    cards = cursor.fetchall()
    
    print(f"Processing {len(cards)} cards from deck '{deck_name}'...")
    
    updated_count = 0
    skipped_count = 0
    
    # Loop through each card and update the `src` attribute
    for card_id, deck_id, fields, note_id in cards:
        print(f"\nProcessing card ID: {card_id}, Note ID: {note_id}")
        
        # Check if there are any image tags that need updating
        img_tags = re.findall(r'<img src="([^"]+)"', fields)
        needs_update = False
        
        if not img_tags:
            print("  No image tags found in this card.")
            skipped_count += 1
            continue
            
        for img_src in img_tags:
            if not img_src.startswith("resized_"):
                print(f"  Found image without 'resized_' prefix: {img_src}")
                needs_update = True
            else:
                print(f"  Image already has 'resized_' prefix: {img_src}")
        
        if needs_update:
            # Use regex to find and replace only src attributes that don't start with resized_
            updated_fields = re.sub(
                r'<img src="(?!resized_)([^"]+)"',
                r'<img src="resized_\1"',
                fields
            )
            
            # Update the fields back into the database
            update_query = "UPDATE notes SET flds = ? WHERE id = ?;"
            cursor.execute(update_query, (updated_fields, note_id))
            updated_count += 1
            print("  Card updated successfully.")
        else:
            print("  No updates needed for this card.")
            skipped_count += 1
    
    # Commit the changes
    conn.commit()
    return updated_count, skipped_count

# Execute the function
updated_count, skipped_count = update_image_src()

# Output the result
print("\n--- SUMMARY ---")
print(f"Total updated cards: {updated_count}")
print(f"Total skipped cards (no changes needed): {skipped_count}")
print(f"Total cards processed: {updated_count + skipped_count}")

# Close the connection
conn.close()