"""
Add `course_item_id` TEXT column to the `course_items` table and populate
existing rows with 32-char hex UUIDs (uuid4.hex). Also create a unique index.

Usage (PowerShell):
    # Stop the Flask server first!
    python .\scripts\add_course_item_id.py

The script will look for DATABASE_URL environment variable. If that is set and
starts with "sqlite:///" it will use the local path after that prefix. Otherwise
it defaults to './data.db'.

This script is intended for development use only.
"""
import sqlite3
import uuid
import os
import sys

# Determine DB path (match app.py behavior)
env_db = os.getenv("DATABASE_URL")
if env_db and env_db.startswith("sqlite:///"):
    db_path = env_db[len("sqlite:///"):]
elif env_db and env_db.endswith('.db'):
    db_path = env_db
else:
    db_path = os.path.join(os.getcwd(), "data.db")

if not os.path.exists(db_path):
    print(f"Database file not found: {db_path}")
    print("Start the app once to create the DB, or point DATABASE_URL to an existing file.")
    sys.exit(1)

print(f"Opening SQLite DB at: {db_path}")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

try:
    # Try to add the column. If it exists, this will raise an OperationalError.
    print("Adding column course_item_id (if not exists)...")
    cur.execute("ALTER TABLE course_items ADD COLUMN course_item_id TEXT;")
    conn.commit()
    print("Column added.")
except Exception as e:
    # SQLite raises sqlite3.OperationalError if column already exists
    print(f"Could not add column (it may already exist): {e}")

# Populate NULL / empty values with uuid4 hex
print("Populating missing course_item_id values...")
cur.execute("SELECT id, course_item_id FROM course_items")
rows = cur.fetchall()
updated = 0
for row in rows:
    row_id, existing = row
    if existing is None or str(existing).strip() == "":
        new_uuid = uuid.uuid4().hex
        cur.execute(
            "UPDATE course_items SET course_item_id = ? WHERE id = ?",
            (new_uuid, row_id),
        )
        updated += 1

conn.commit()
print(f"Populated {updated} rows with new UUIDs.")

# Create unique index to enforce uniqueness on new column
try:
    print("Creating unique index on course_item_id (if not exists)...")
    cur.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_course_items_course_item_id ON course_items(course_item_id)"
    )
    conn.commit()
    print("Index created/ensured.")
except Exception as e:
    print(f"Could not create index: {e}")

cur.close()
conn.close()
print("Done. Restart your Flask server and test endpoints.")
