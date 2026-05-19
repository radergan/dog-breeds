"""
Migrate data from local SQLite database to Supabase
Run this after setting up your Supabase project and running the schema
"""
import os
import sqlite3
from supabase import create_client, Client

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # Use service role key for admin operations

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables")
    print("Example:")
    print('  $env:SUPABASE_URL="https://xxxxx.supabase.co"')
    print('  $env:SUPABASE_SERVICE_KEY="your-service-role-key"')
    exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Connect to local SQLite database
conn = sqlite3.connect('dog_breeds.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def migrate_breeds():
    """Migrate breeds from SQLite to Supabase"""
    print("\nMigrating breeds...")
    
    cursor.execute('SELECT * FROM breeds')
    breeds = cursor.fetchall()
    
    migrated = 0
    for breed in breeds:
        breed_data = {
            'uuid': breed['uuid'],
            'legacy_id': breed['legacy_id'],
            'name': breed['name'],
            'slug': breed['slug'],
            'group_slug': breed['group_slug'],
            'group_display': breed['group_display'],
            'size': breed['size'],
            'weight': breed['weight'],
            'height': breed['height'],
            'lifespan': breed['lifespan'],
            'temperament': breed['temperament'],
            'energy_level': breed['energy_level'],
            'trainability': breed['trainability'],
            'shedding': breed['shedding'],
            'grooming_needs': breed['grooming_needs'],
            'good_with_kids': bool(breed['good_with_kids']),
            'good_with_pets': bool(breed['good_with_pets']),
            'barking_level': breed['barking_level'],
            'origin': breed['origin'],
            'image_url': breed['image_url'],
            'wikipedia_url': breed['wikipedia_url'],
            'apartment_friendly': bool(breed['apartment_friendly']),
            'first_time_owner': bool(breed['first_time_owner']),
            'tolerates_being_alone': bool(breed['tolerates_being_alone']),
            'good_with_strangers': bool(breed['good_with_strangers']),
            'exercise_needs': breed['exercise_needs']
        }
        
        try:
            result = supabase.table('breeds').insert(breed_data).execute()
            migrated += 1
            print(f"  Migrated: {breed['name']}")
        except Exception as e:
            print(f"  ERROR migrating {breed['name']}: {e}")
    
    print(f"\nMigrated {migrated} breeds")
    return migrated

def migrate_images():
    """Migrate breed images from SQLite to Supabase"""
    print("\nMigrating breed images...")
    
    cursor.execute('SELECT * FROM breed_images')
    images = cursor.fetchall()
    
    migrated = 0
    for img in images:
        img_data = {
            'breed_uuid': img['breed_uuid'],
            'image_url': img['image_url'],
            'caption': img['caption'],
            'source': img['source'],
            'is_primary': bool(img['is_primary'])
        }
        
        try:
            supabase.table('breed_images').insert(img_data).execute()
            migrated += 1
        except Exception as e:
            print(f"  ERROR migrating image: {e}")
    
    print(f"Migrated {migrated} images")

def migrate_videos():
    """Migrate breed videos from SQLite to Supabase"""
    print("\nMigrating breed videos...")
    
    cursor.execute('SELECT * FROM breed_videos')
    videos = cursor.fetchall()
    
    migrated = 0
    for vid in videos:
        vid_data = {
            'breed_uuid': vid['breed_uuid'],
            'platform': vid['platform'],
            'video_id': vid['video_id'],
            'video_url': vid['video_url'],
            'title': vid['title'],
            'thumbnail_url': vid['thumbnail_url'],
            'duration': vid['duration'],
            'is_featured': bool(vid['is_featured'])
        }
        
        try:
            supabase.table('breed_videos').insert(vid_data).execute()
            migrated += 1
        except Exception as e:
            print(f"  ERROR migrating video: {e}")
    
    print(f"Migrated {migrated} videos")

def verify_migration():
    """Verify the migration was successful"""
    print("\nVerifying migration...")
    
    # Count breeds in Supabase
    result = supabase.table('breeds').select('uuid', count='exact').execute()
    breed_count = result.count
    
    # Count in SQLite
    cursor.execute('SELECT COUNT(*) FROM breeds')
    local_count = cursor.fetchone()[0]
    
    print(f"  Local SQLite: {local_count} breeds")
    print(f"  Supabase: {breed_count} breeds")
    
    if breed_count == local_count:
        print("  Migration verified successfully!")
    else:
        print("  WARNING: Counts don't match!")

if __name__ == '__main__':
    print("Starting migration to Supabase...")
    print(f"Target: {SUPABASE_URL}")
    
    try:
        migrate_breeds()
        migrate_images()
        migrate_videos()
        verify_migration()
        
        print("\nMigration complete!")
        print("\nNext steps:")
        print("1. Update frontend to use Supabase client")
        print("2. Test queries in Supabase dashboard")
        print("3. Deploy to production")
        
    except Exception as e:
        print(f"\nERROR: Migration failed - {e}")
    finally:
        conn.close()
