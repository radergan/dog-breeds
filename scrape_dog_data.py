import requests
import json
import time
from bs4 import BeautifulSoup

# AKC Groups for hierarchical navigation (like your primate families)
AKC_GROUPS = {
    'sporting': 'Sporting Group',
    'hound': 'Hound Group',
    'working': 'Working Group',
    'terrier': 'Terrier Group',
    'toy': 'Toy Group',
    'non-sporting': 'Non-Sporting Group',
    'herding': 'Herding Group',
    'foundation': 'Foundation Stock Service'
}

def scrape_akc_breeds():
    """Scrape breed list from AKC"""
    print("Fetching breed list from AKC...")
    
    # This would scrape from AKC website or use an API
    # For now, let's create a starter dataset with popular breeds
    breeds = [
        # Sporting Group
        {'name': 'Golden Retriever', 'group': 'sporting'},
        {'name': 'Labrador Retriever', 'group': 'sporting'},
        {'name': 'Cocker Spaniel', 'group': 'sporting'},
        {'name': 'English Springer Spaniel', 'group': 'sporting'},
        {'name': 'Irish Setter', 'group': 'sporting'},
        
        # Hound Group
        {'name': 'Beagle', 'group': 'hound'},
        {'name': 'Bloodhound', 'group': 'hound'},
        {'name': 'Dachshund', 'group': 'hound'},
        {'name': 'Basset Hound', 'group': 'hound'},
        {'name': 'Greyhound', 'group': 'hound'},
        
        # Working Group
        {'name': 'Siberian Husky', 'group': 'working'},
        {'name': 'Boxer', 'group': 'working'},
        {'name': 'Great Dane', 'group': 'working'},
        {'name': 'Rottweiler', 'group': 'working'},
        {'name': 'Bernese Mountain Dog', 'group': 'working'},
        
        # Terrier Group
        {'name': 'Bull Terrier', 'group': 'terrier'},
        {'name': 'Scottish Terrier', 'group': 'terrier'},
        {'name': 'West Highland White Terrier', 'group': 'terrier'},
        {'name': 'Yorkshire Terrier', 'group': 'terrier'},
        {'name': 'American Staffordshire Terrier', 'group': 'terrier'},
        
        # Toy Group
        {'name': 'Chihuahua', 'group': 'toy'},
        {'name': 'Pomeranian', 'group': 'toy'},
        {'name': 'Pug', 'group': 'toy'},
        {'name': 'Shih Tzu', 'group': 'toy'},
        {'name': 'Maltese', 'group': 'toy'},
        
        # Non-Sporting Group
        {'name': 'French Bulldog', 'group': 'non-sporting'},
        {'name': 'Poodle', 'group': 'non-sporting'},
        {'name': 'Bulldog', 'group': 'non-sporting'},
        {'name': 'Boston Terrier', 'group': 'non-sporting'},
        {'name': 'Dalmatian', 'group': 'non-sporting'},
        
        # Herding Group
        {'name': 'German Shepherd', 'group': 'herding'},
        {'name': 'Border Collie', 'group': 'herding'},
        {'name': 'Australian Shepherd', 'group': 'herding'},
        {'name': 'Pembroke Welsh Corgi', 'group': 'herding'},
        {'name': 'Shetland Sheepdog', 'group': 'herding'},
    ]
    
    return breeds

def get_breed_details(breed_name, group):
    """Get detailed information about a breed from Wikipedia/Dog API"""
    print(f"  Fetching details for {breed_name}...")
    
    # Wikipedia API search
    wiki_search = requests.get(
        'https://en.wikipedia.org/w/api.php',
        params={
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': f'{breed_name} dog breed',
            'srlimit': 1
        }
    )
    
    wikipedia_url = None
    if wiki_search.status_code == 200:
        results = wiki_search.json().get('query', {}).get('search', [])
        if results:
            page_title = results[0]['title']
            wikipedia_url = f"http://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
    
    # Try to get image from Wikipedia Commons
    image = f"https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/{breed_name.replace(' ', '_')}.jpg/440px-{breed_name.replace(' ', '_')}.jpg"
    
    # Default breed characteristics (would be scraped from AKC or other sources)
    # These are placeholders - would need real data
    size_map = {
        'Chihuahua': 'Toy', 'Pomeranian': 'Toy', 'Pug': 'Small', 'Shih Tzu': 'Small', 'Maltese': 'Toy',
        'Yorkshire Terrier': 'Toy', 'French Bulldog': 'Small', 'Boston Terrier': 'Small',
        'Beagle': 'Medium', 'Cocker Spaniel': 'Medium', 'Bulldog': 'Medium', 'Border Collie': 'Medium',
        'Australian Shepherd': 'Medium', 'Boxer': 'Large', 'Golden Retriever': 'Large', 
        'Labrador Retriever': 'Large', 'German Shepherd': 'Large', 'Rottweiler': 'Large',
        'Great Dane': 'Giant', 'Bernese Mountain Dog': 'Large', 'Siberian Husky': 'Medium'
    }
    
    energy_map = {
        'Border Collie': 'Very High', 'Australian Shepherd': 'Very High', 'Siberian Husky': 'Very High',
        'Labrador Retriever': 'High', 'Golden Retriever': 'High', 'Boxer': 'High',
        'Bulldog': 'Low', 'Pug': 'Low', 'Basset Hound': 'Low', 'Great Dane': 'Moderate'
    }
    
    return {
        'size': size_map.get(breed_name, 'Medium'),
        'energy_level': energy_map.get(breed_name, 'Moderate'),
        'temperament': 'Friendly, loyal, and intelligent',  # Placeholder
        'good_with_kids': True,  # Placeholder
        'good_with_pets': True,  # Placeholder
        'grooming_needs': 'Moderate',  # Placeholder
        'trainability': 'High',  # Placeholder
        'shedding': 'Moderate',  # Placeholder
        'lifespan': '10-13 years',  # Placeholder
        'image': image,
        'wikipedia_url': wikipedia_url,
        'origin': 'United States'  # Placeholder
    }

def build_dog_database():
    """Build complete dog breed database"""
    print("Building dog breed database...\n")
    
    breeds = scrape_akc_breeds()
    database = []
    
    for i, breed in enumerate(breeds):
        print(f"[{i+1}/{len(breeds)}] {breed['name']}")
        
        details = get_breed_details(breed['name'], breed['group'])
        
        entry = {
            'id': i + 1,
            'name': breed['name'],
            'group': breed['group'],
            'groupDisplay': AKC_GROUPS[breed['group']],
            'size': details['size'],
            'energyLevel': details['energy_level'],
            'temperament': details['temperament'],
            'goodWithKids': details['good_with_kids'],
            'goodWithPets': details['good_with_pets'],
            'groomingNeeds': details['grooming_needs'],
            'trainability': details['trainability'],
            'shedding': details['shedding'],
            'lifespan': details['lifespan'],
            'image': details['image'],
            'images': [details['image']],  # Will be enriched later with more photos
            'wikipediaUrl': details['wikipedia_url'],
            'origin': details['origin']
        }
        
        database.append(entry)
        time.sleep(0.5)  # Rate limiting
    
    # Save to JSON
    with open('dog_breeds.json', 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Successfully created database with {len(database)} breeds")
    print("Saved to: dog_breeds.json")
    
    return database

if __name__ == '__main__':
    database = build_dog_database()
    
    # Print summary
    print("\n📊 Summary by Group:")
    groups = {}
    for breed in database:
        group = breed['groupDisplay']
        groups[group] = groups.get(group, 0) + 1
    
    for group, count in sorted(groups.items()):
        print(f"  {group}: {count} breeds")
