# Supabase Setup Guide

## Step 1: Create Supabase Account
1. Go to https://supabase.com
2. Sign up with GitHub (easiest)
3. Create a new project
   - Choose a project name: `dog-breeds`
   - Set a strong database password (save it!)
   - Choose region closest to you

## Step 2: Get Your Credentials
Once project is created:
1. Go to Project Settings > API
2. Save these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGc...` (safe for client-side)
   - **service_role key**: `eyJhbGc...` (SECRET - server-side only)

## Step 3: Run Migration Script
```bash
# Install Supabase Python client
pip install supabase

# Set environment variables
$env:SUPABASE_URL="your-project-url"
$env:SUPABASE_KEY="your-service-role-key"

# Run migration
python migrate_to_supabase.py
```

## Step 4: Update Frontend
The frontend will use the Supabase JavaScript client to query data directly:
```html
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script>
const supabase = window.supabase.createClient(
  'YOUR_SUPABASE_URL',
  'YOUR_ANON_KEY'
)

// Query breeds
const { data: breeds } = await supabase
  .from('breeds')
  .select('*')
</script>
```

## Environment Variables
Create `.env` file:
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc... (DO NOT COMMIT THIS)
```

Add `.env` to `.gitignore`

## Benefits
- No more Python export scripts
- Frontend queries database directly
- Real-time updates possible
- Built-in authentication ready
- Free tier: 500MB database, 2GB file storage
- Auto-backups included
