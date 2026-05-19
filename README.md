# Dog Breed Finder

A comprehensive database of 277 AKC dog breeds with filtering, search, and individual breed pages.

🌐 **Live Site**: [https://yourusername.github.io/dog-breeds](https://yourusername.github.io/dog-breeds)
🗄️ **Database**: Supabase (PostgreSQL)

## Features

- 🔍 **Search** by breed name
- 📊 **Filter** by size, AKC group, shedding, temperament
- 📄 **277 Individual breed pages** with detailed information
- 📱 **Responsive design** with Spectre.css
- 🎨 **Custom dog icons** with size badges
- 🔐 **User authentication** ready (Supabase Auth)
- 💾 **PostgreSQL database** with Supabase

## Data Source

Built from the [Kaggle Dog Breeds Dataset](https://www.kaggle.com/datasets/mexwell/dog-breeds-dataset) with 277 AKC breeds and 21 attributes including:
- Physical traits (size, weight, height, lifespan)
- Temperament and behavior
- Grooming and shedding needs
- Energy level and trainability

## Local Development

### Setup
```bash
git clone https://github.com/yourusername/dog-breeds.git
cd dog-breeds
```

### View Site Locally
Simply open `index.html` in your browser, or use a local server:
```bash
# Python 3
python -m http.server 8000

# Node.js
npx http-server

# VS Code
# Install "Live Server" extension and click "Go Live"
```

Visit: `http://localhost:8000`

## Supabase Setup (Database)

This project uses Supabase (PostgreSQL) for production database hosting.

### Quick Setup

1. **Create Supabase account**: https://supabase.com
2. **Create new project** (save database password!)
3. **Run SQL schema**:
   - Go to SQL Editor in Supabase dashboard
   - Copy/paste contents of `supabase_schema.sql`
   - Run query
4. **Set environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```
5. **Migrate data** (optional):
   ```bash
   pip install supabase
   python migrate_to_supabase.py
   ```

See [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for detailed instructions.

### Managing Data

The site uses a SQLite database for data management:

```bash
# Install dependencies
pip install kagglehub

# Create/update database
python database_setup.py

# Add videos or images using Python API
python breed_db.py

# Export to JavaScript for website
python export_db_to_js.py
```

See [DATABASE_README.md](DATABASE_README.md) for full database documentation.

## Deployment

### GitHub Pages (Recommended)

1. **Push to GitHub:**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: Deploy from branch `main`
   - Folder: `/ (root)`
   - Save

3. **Access your site:**
   - `https://yourusername.github.io/dog-breeds`
   - Custom domain supported (configure in Settings)

### Other Hosting Options
- **Netlify**: Drag & drop the folder
- **Vercel**: Import GitHub repo
- **Cloudflare Pages**: Connect GitHub repo

All are free for static sites!

## Project Structure

```
dog-breeds/
├── index.html              # Main browse page with filters
├── dogs.js                 # Breed data (generated from database)
├── app.js                  # Client-side filtering logic
├── breeds/                 # Individual breed pages
│   ├── golden-retriever.html
│   ├── labrador-retriever.html
│   └── ... (277 total)
├── assets/
│   └── tiles/
│       ├── small-dog.png
│       ├── medium-dog.png
│       └── large-dog.png
├── database_setup.py       # Create/populate SQLite database
├── breed_db.py            # Python API for database
├── export_db_to_js.py     # Export database to dogs.js
├── generate_breed_pages.py # Generate 277 HTML pages
└── process_kaggle_dataset.py # Process CSV → JSON
```

## Adding Content

### Add Videos to Breeds
```python
from breed_db import BreedDB

db = BreedDB()
golden = db.get_breed_by_slug('golden-retriever')

db.add_breed_video(
    breed_uuid=golden['uuid'],
    platform='youtube',
    video_id='abc123',
    video_url='https://youtube.com/watch?v=abc123',
    title='Golden Retriever Playing'
)

# Export to dogs.js for website
# Run: python export_db_to_js.py
```

### Add Images to Breeds
```python
db.add_breed_image(
    breed_uuid=golden['uuid'],
    image_url='https://example.com/golden-retriever.jpg',
    caption='Golden Retriever in field',
    is_primary=True
)
```

### Regenerate Static Site
After updating the database:
```bash
python export_db_to_js.py      # Update dogs.js
python generate_breed_pages.py  # Regenerate breed pages (if needed)
git add .
git commit -m "Update breed data"
git push  # Auto-deploys to GitHub Pages
```

## Future Features

- [ ] User comments (via Utterances or Supabase)
- [ ] Breed comparison tool
- [ ] Favorites/bookmarks (localStorage)
- [ ] Curated video galleries
- [ ] Professional breed photos
- [ ] Breeder directory
- [ ] Quiz: "Which breed is right for you?"

## Tech Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **CSS Framework**: [Spectre.css](https://picturepan2.github.io/spectre/)
- **Database**: SQLite (local development)
- **Data Format**: JSON (exported for static site)
- **Hosting**: GitHub Pages (or Netlify/Vercel)

## License

Data sourced from [Kaggle Dog Breeds Dataset](https://www.kaggle.com/datasets/mexwell/dog-breeds-dataset) by mexwell.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Update the database using Python scripts
4. Export to dogs.js
5. Submit a pull request

---

Built with 🐕 by [Your Name]
