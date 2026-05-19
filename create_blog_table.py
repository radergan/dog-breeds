"""Create blog_posts table in database"""
import sqlite3

conn = sqlite3.connect('dog_breeds.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS blog_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        excerpt TEXT,
        featured_image TEXT,
        published_date TEXT NOT NULL,
        author TEXT DEFAULT 'Admin',
        category TEXT,
        tags TEXT,
        is_published INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()

print("Blog posts table created successfully")
