# Dog Breeds Database

SQLite database setup for the Dog Breeds project with UUIDs, proper schema, and support for future features like comments and videos.

## Quick Start

### 1. Create and Populate Database

```bash
python database_setup.py
```

This will:
- Create `dog_breeds.db` SQLite database
- Migrate all 277 breeds from `dog_breeds_kaggle.json`
- Assign unique UUIDs to each breed
- Export enriched JSON with UUIDs to `dog_breeds_with_uuids.json`

### 2. Query the Database

```python
from breed_db import BreedDB

db = BreedDB()

# Get all breeds
breeds = db.get_all_breeds()

# Search by name
results = db.search_breeds('Golden')

# Filter by criteria
small_friendly = db.filter_breeds(
    size='Small',
    good_with_kids=True,
    shedding='Non-Shedding'
)

# Get specific breed
golden = db.get_breed_by_slug('golden-retriever')
print(golden['uuid'])  # e.g., 'a3f8d9e2-1c4b-4d5e-9f8a-7b6c5d4e3f2a'
```

## Database Schema

### breeds
Main table with all breed information
- `uuid` (PRIMARY KEY) - Unique identifier for each breed
- `legacy_id` - Original sequential ID from JSON
- `name` - Breed name
- `slug` - URL-friendly slug
- `group_slug` / `group_display` - AKC group
- `size`, `weight`, `height`, `lifespan`
- `temperament`, `energy_level`, `trainability`
- `shedding`, `grooming_needs`, `barking_level`
- `good_with_kids`, `good_with_pets` (BOOLEAN)
- `apartment_friendly`, `first_time_owner`, etc.
- Timestamps: `created_at`, `updated_at`

### breed_images
One-to-many: Store multiple images per breed
- `breed_uuid` (FOREIGN KEY)
- `image_url`, `caption`, `source`
- `is_primary` - Mark main image

### breed_videos
Store curated videos (YouTube, TikTok, etc.)
- `breed_uuid` (FOREIGN KEY)
- `platform` - 'youtube', 'tiktok', etc.
- `video_id`, `video_url`, `title`, `thumbnail_url`
- `duration` (seconds)
- `is_featured` - Mark featured video

### comments
User comments (for future feature)
- `breed_uuid` (FOREIGN KEY)
- `user_name`, `user_email`, `comment_text`
- `rating` (1-5)
- `is_approved` - Moderation flag

## Python API Usage

### Adding Videos

```python
db = BreedDB()

# Get breed UUID
golden = db.get_breed_by_slug('golden-retriever')

# Add YouTube video
db.add_breed_video(
    breed_uuid=golden['uuid'],
    platform='youtube',
    video_id='dQw4w9WgXcQ',
    video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    title='Golden Retriever Puppy Playing',
    thumbnail_url='https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg',
    duration=180,
    is_featured=True
)

# Get all videos for breed
videos = db.get_breed_videos(golden['uuid'])
```

### Adding Comments

```python
# User submits comment (needs approval)
comment_id = db.add_comment(
    breed_uuid=golden['uuid'],
    comment_text='Best dog ever! So friendly and smart.',
    user_name='John Doe',
    rating=5
)

# Admin approves comment
db.approve_comment(comment_id)

# Get approved comments
comments = db.get_breed_comments(golden['uuid'], approved_only=True)
```

### Filtering Breeds

```python
# Multiple filters
apartment_dogs = db.filter_breeds(
    size='Small',
    good_with_kids=True,
    shedding='Non-Shedding'
)

# By size
small = db.get_breeds_by_size('Small')

# By group
sporting = db.get_breeds_by_group('sporting')

# Search
labs = db.search_breeds('Labrador')
```

## Next Steps

### Option 1: Keep Static Files (Current)
- Continue using static HTML/JS
- Generate static JSON from database for client-side filtering
- Use Python scripts to manage database
- Good for: Simple deployment, no server needed

### Option 2: Add Python Backend (Flask/FastAPI)
- Create REST API endpoints
- Enable real-time comments, favorites, etc.
- Good for: Interactive features, user accounts

### Option 3: Migrate to Supabase/Firebase
- PostgreSQL with UUIDs (Supabase)
- Real-time sync, authentication, storage
- Good for: Scaling, collaboration, hosted solution

## Files

- `database_setup.py` - Initialize database, migrate JSON data
- `breed_db.py` - Data access layer (API for querying)
- `dog_breeds.db` - SQLite database file
- `dog_breeds_with_uuids.json` - Export with UUIDs

## Why UUIDs?

UUIDs (Universally Unique Identifiers) instead of sequential IDs:
- **Portable**: Can merge databases without conflicts
- **Secure**: Can't guess other breed IDs
- **Future-proof**: Works with distributed systems
- **URLs**: Can use in URLs for SEO-friendly pages

Example: `/breeds/a3f8d9e2-1c4b-4d5e-9f8a-7b6c5d4e3f2a` or still use slug `/breeds/golden-retriever`
