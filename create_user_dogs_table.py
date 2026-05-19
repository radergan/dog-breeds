"""
Migration script to create user_dogs table for dog profile feature
"""
import sqlite3
from datetime import datetime

def create_user_dogs_table():
    """Create the user_dogs table in dog_breeds.db"""
    conn = sqlite3.connect('dog_breeds.db')
    cursor = conn.cursor()
    
    # Create user_dogs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_dogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            breed_uuid TEXT NOT NULL,
            name TEXT NOT NULL,
            birthdate TEXT,
            weight REAL,
            photo_url TEXT,
            is_public INTEGER DEFAULT 0,
            public_comment TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (breed_uuid) REFERENCES breeds (uuid) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for better query performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_dogs_user_id ON user_dogs(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_dogs_breed_uuid ON user_dogs(breed_uuid)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_dogs_public ON user_dogs(is_public, status)')
    
    conn.commit()
    print("✓ Created user_dogs table successfully")
    
    # Show table structure
    cursor.execute("PRAGMA table_info(user_dogs)")
    columns = cursor.fetchall()
    print("\nTable structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == '__main__':
    create_user_dogs_table()
