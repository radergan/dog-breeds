-- Supabase Database Schema for Dog Breeds

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Breeds table
CREATE TABLE breeds (
    uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
    good_with_kids BOOLEAN DEFAULT FALSE,
    good_with_pets BOOLEAN DEFAULT FALSE,
    barking_level TEXT,
    origin TEXT,
    image_url TEXT,
    wikipedia_url TEXT,
    apartment_friendly BOOLEAN DEFAULT FALSE,
    first_time_owner BOOLEAN DEFAULT FALSE,
    tolerates_being_alone BOOLEAN DEFAULT FALSE,
    good_with_strangers BOOLEAN DEFAULT FALSE,
    exercise_needs TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Breed images table
CREATE TABLE breed_images (
    id SERIAL PRIMARY KEY,
    breed_uuid UUID REFERENCES breeds(uuid) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    caption TEXT,
    source TEXT,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Breed videos table
CREATE TABLE breed_videos (
    id SERIAL PRIMARY KEY,
    breed_uuid UUID REFERENCES breeds(uuid) ON DELETE CASCADE,
    platform TEXT,
    video_id TEXT,
    video_url TEXT,
    title TEXT,
    thumbnail_url TEXT,
    duration INTEGER,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User comments table (for future use)
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    breed_uuid UUID REFERENCES breeds(uuid) ON DELETE CASCADE,
    user_name TEXT,
    user_email TEXT,
    comment_text TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_breeds_slug ON breeds(slug);
CREATE INDEX idx_breeds_name ON breeds(name);
CREATE INDEX idx_breeds_group ON breeds(group_slug);
CREATE INDEX idx_breeds_size ON breeds(size);
CREATE INDEX idx_breed_images_breed_uuid ON breed_images(breed_uuid);
CREATE INDEX idx_breed_videos_breed_uuid ON breed_videos(breed_uuid);
CREATE INDEX idx_comments_breed_uuid ON comments(breed_uuid);

-- Enable Row Level Security (RLS)
ALTER TABLE breeds ENABLE ROW LEVEL SECURITY;
ALTER TABLE breed_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE breed_videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;

-- Public read access for breeds
CREATE POLICY "Enable read access for all users" ON breeds
    FOR SELECT USING (true);

-- Public read access for breed images
CREATE POLICY "Enable read access for all users" ON breed_images
    FOR SELECT USING (true);

-- Public read access for breed videos
CREATE POLICY "Enable read access for all users" ON breed_videos
    FOR SELECT USING (true);

-- Public read access for approved comments only
CREATE POLICY "Enable read access for approved comments" ON comments
    FOR SELECT USING (is_approved = true);

-- Admin write access (will configure with service role)
