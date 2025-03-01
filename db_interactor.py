import sqlite3
import os


# Path to the Anki database
db_path = "./collection.anki2"

def unicase_collation(str1, str2):
    if str1 is None and str2 is None:
        return 0
    elif str1 is None:
        return -1
    elif str2 is None:
        return 1
    return (str1.casefold() > str2.casefold()) - (str1.casefold() < str2.casefold())

conn = sqlite3.connect(db_path)
conn.create_collation("unicase", unicase_collation)  # Register the custom collation
cursor = conn.cursor()

# Query 1: Total cards in the deck
query_1 = """
SELECT COUNT(*)
FROM cards
WHERE did = (SELECT id FROM decks WHERE name = "Core_2k_6k_Japanese_Deck");
"""

# Query 2: Completed cards in the deck
query_2 = """
SELECT COUNT(*)
FROM cards
WHERE did = (SELECT id FROM decks WHERE name = "Core_2k_6k_Japanese_Deck")
  AND queue = 2;
"""

# Query 3: Retrieve fields from notes
retrive_field_query = """
SELECT n.flds
FROM notes n
JOIN cards c ON c.nid = n.id
WHERE c.did = (SELECT id FROM decks WHERE name = "Core_2k_6k_Japanese_Deck")
LIMIT 10;
"""

# Execute and print the results
for query in [query_1, query_2, retrive_field_query]:
    print("||___" * 6)
    cursor.execute(query)
    results = cursor.fetchall()
    for row in results:
        print(row)

conn.close()