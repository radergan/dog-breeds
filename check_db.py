from breed_db import BreedDB

db = BreedDB()
breed = db.get_breed_by_slug('affenpinscher')
print(f"Image URL in database: {breed['image_url']}")
