"""
Database setup for Dog Breeds
Migrates JSON data to SQLite with proper schema and UUIDs
"""
import sqlite3
import json
import uuid
from datetime import datetime

# Database file
DB_FILE = 'dog_breeds.db'

def create_database():
    """Create SQLite database with proper schema"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Main breeds table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS breeds (
        uuid TEXT PRIMARY KEY,
        legacy_id INTEGER,
        name TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        group_slug TEXT,
        group_display TEXT,
        size TEXT,
        weight TEXT,
        height TEXT,
        lifespan TEXT,
        temperament TEXT,
        energy_level TEXT,
        trainability TEXT,
        shedding TEXT,
        grooming_needs TEXT,
        good_with_kids BOOLEAN,
        good_with_pets BOOLEAN,
        barking_level TEXT,
        origin TEXT,
        image_url TEXT,
        wikipedia_url TEXT,
        apartment_friendly TEXT,
        first_time_owner TEXT,
        tolerates_being_alone TEXT,
        good_with_strangers TEXT,
        exercise_needs TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Images table (one-to-many relationship)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS breed_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        breed_uuid TEXT NOT NULL,
        image_url TEXT NOT NULL,
        caption TEXT,
        source TEXT,
        is_primary BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (breed_uuid) REFERENCES breeds(uuid) ON DELETE CASCADE
    )
    ''')
    
    # Videos table for curated videos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS breed_videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        breed_uuid TEXT NOT NULL,
        platform TEXT NOT NULL, -- 'youtube', 'tiktok', etc.
        video_id TEXT NOT NULL,
        video_url TEXT NOT NULL,
        title TEXT,
        thumbnail_url TEXT,
        duration INTEGER, -- in seconds
        is_featured BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (breed_uuid) REFERENCES breeds(uuid) ON DELETE CASCADE
    )
    ''')
    
    # Comments table (for future feature)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        breed_uuid TEXT NOT NULL,
        user_name TEXT,
        user_email TEXT,
        comment_text TEXT NOT NULL,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        is_approved BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (breed_uuid) REFERENCES breeds(uuid) ON DELETE CASCADE
    )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_breeds_name ON breeds(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_breeds_slug ON breeds(slug)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_breeds_group ON breeds(group_slug)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_breeds_size ON breeds(size)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_breed ON comments(breed_uuid)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_approved ON comments(is_approved)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created: {DB_FILE}")


def create_slug(name):
    """Convert breed name to URL-friendly slug"""
    return name.lower().replace(' ', '-').replace('(', '').replace(')', '')


def migrate_json_to_db(json_file='dog_breeds_kaggle.json'):
    """Migrate JSON data to SQLite database with UUIDs"""
    print(f"\n📦 Migrating {json_file} to database...\n")
    
    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        breeds = json.load(f)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    migrated_count = 0
    skipped_count = 0
    
    for breed in breeds:
        slug = create_slug(breed['name'])
        
        # Check if breed already exists
        cursor.execute('SELECT uuid FROM breeds WHERE slug = ?', (slug,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⏭️  Skipping {breed['name']} (already exists)")
            skipped_count += 1
            continue
        
        # Generate UUID for this breed
        breed_uuid = str(uuid.uuid4())
        
        # Insert breed
        cursor.execute('''
        INSERT INTO breeds (
            uuid, legacy_id, name, slug,
            group_slug, group_display, size, weight, height, lifespan,
            temperament, energy_level, trainability, shedding, grooming_needs,
            good_with_kids, good_with_pets, barking_level, origin,
            image_url, wikipedia_url,
            apartment_friendly, first_time_owner, tolerates_being_alone,
            good_with_strangers, exercise_needs
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            breed_uuid,
            breed['id'],
            breed['name'],
            slug,
            breed.get('group'),
            breed.get('groupDisplay'),
            breed.get('size'),
            breed.get('weight'),
            breed.get('height'),
            breed.get('lifespan'),
            breed.get('temperament'),
            breed.get('energyLevel'),
            breed.get('trainability'),
            breed.get('shedding'),
            breed.get('groomingNeeds'),
            breed.get('goodWithKids'),
            breed.get('goodWithPets'),
            breed.get('barkingLevel'),
            breed.get('origin'),
            breed.get('image'),
            breed.get('wikipediaUrl'),
            breed.get('apartmentFriendly'),
            breed.get('firstTimeOwner'),
            breed.get('toleratesBeingAlone'),
            breed.get('goodWithStrangers'),
            breed.get('exerciseNeeds')
        ))
        
        # Insert images if they exist
        if breed.get('images'):
            for img_url in breed['images']:
                cursor.execute('''
                INSERT INTO breed_images (breed_uuid, image_url)
                VALUES (?, ?)
                ''', (breed_uuid, img_url))
        
        migrated_count += 1
        print(f"✅ {breed['name']} → {breed_uuid}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Migration complete!")
    print(f"   Migrated: {migrated_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Total: {migrated_count + skipped_count}\n")


def export_with_uuids(output_file='dog_breeds_with_uuids.json'):
    """Export database back to JSON with UUIDs"""
    print(f"\n📤 Exporting database to {output_file}...\n")
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM breeds ORDER BY name')
    rows = cursor.fetchall()
    
    breeds = []
    for row in rows:
        breed = {
            'uuid': row['uuid'],
            'id': row['legacy_id'],
            'name': row['name'],
            'slug': row['slug'],
            'group': row['group_slug'],
            'groupDisplay': row['group_display'],
            'size': row['size'],
            'weight': row['weight'],
            'height': row['height'],
            'lifespan': row['lifespan'],
            'temperament': row['temperament'],
            'energyLevel': row['energy_level'],
            'trainability': row['trainability'],
            'shedding': row['shedding'],
            'groomingNeeds': row['grooming_needs'],
            'goodWithKids': bool(row['good_with_kids']),
            'goodWithPets': bool(row['good_with_pets']),
            'barkingLevel': row['barking_level'],
            'origin': row['origin'],
            'image': row['image_url'],
            'images': [],
            'wikipediaUrl': row['wikipedia_url'],
            'apartmentFriendly': row['apartment_friendly'],
            'firstTimeOwner': row['first_time_owner'],
            'toleratesBeingAlone': row['tolerates_being_alone'],
            'goodWithStrangers': row['good_with_strangers'],
            'exerciseNeeds': row['exercise_needs']
        }
        
        # Get images for this breed
        cursor.execute(
            'SELECT image_url FROM breed_images WHERE breed_uuid = ?',
            (row['uuid'],)
        )
        images = cursor.fetchall()
        breed['images'] = [img['image_url'] for img in images]
        
        breeds.append(breed)
    
    conn.close()
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(breeds, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exported {len(breeds)} breeds to {output_file}\n")


def show_stats():
    """Show database statistics"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM breeds')
    total_breeds = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM breed_images')
    total_images = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM breed_videos')
    total_videos = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM comments WHERE is_approved = 1')
    approved_comments = cursor.fetchone()[0]
    
    cursor.execute('SELECT size, COUNT(*) as count FROM breeds GROUP BY size')
    size_breakdown = cursor.fetchall()
    
    conn.close()
    
    print("\n📊 Database Statistics")
    print("=" * 40)
    print(f"Total Breeds:       {total_breeds}")
    print(f"Total Images:       {total_images}")
    print(f"Total Videos:       {total_videos}")
    print(f"Approved Comments:  {approved_comments}")
    print("\nBreeds by Size:")
    for size, count in size_breakdown:
        print(f"  {size}: {count}")
    print("=" * 40 + "\n")


if __name__ == '__main__':
    print("🐕 Dog Breeds Database Setup\n")
    
    # Step 1: Create database schema
    create_database()
    
    # Step 2: Migrate JSON data
    migrate_json_to_db()
    
    # Step 3: Export with UUIDs (optional, for reference)
    export_with_uuids()
    
    # Step 4: Show stats
    show_stats()
    
    print("✅ Database setup complete!\n")
    print(f"📁 Database file: {DB_FILE}")
    print(f"📄 JSON export: dog_breeds_with_uuids.json\n")
