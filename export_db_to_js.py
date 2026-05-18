"""
Export database to JavaScript format for static site
Generates dogs.js with UUIDs included
"""
from breed_db import BreedDB
import json

def export_to_js(output_file='dogs.js'):
    """Export database to JavaScript format"""
    print(f"📤 Exporting database to {output_file}...\n")
    
    db = BreedDB()
    breeds = db.get_all_breeds()
    
    # Convert database format to JS format
    js_breeds = []
    for breed in breeds:
        js_breed = {
            'uuid': breed['uuid'],
            'id': breed['legacy_id'],
            'name': breed['name'],
            'slug': breed['slug'],
            'group': breed['group_slug'],
            'groupDisplay': breed['group_display'],
            'size': breed['size'],
            'weight': breed['weight'],
            'height': breed['height'],
            'lifespan': breed['lifespan'],
            'temperament': breed['temperament'],
            'energyLevel': breed['energy_level'],
            'trainability': breed['trainability'],
            'shedding': breed['shedding'],
            'groomingNeeds': breed['grooming_needs'],
            'goodWithKids': bool(breed['good_with_kids']),
            'goodWithPets': bool(breed['good_with_pets']),
            'barkingLevel': breed['barking_level'],
            'origin': breed['origin'],
            'image': breed['image_url'],
            'images': [],  # TODO: Load from breed_images table
            'wikipediaUrl': breed['wikipedia_url'],
            'apartmentFriendly': breed['apartment_friendly'],
            'firstTimeOwner': breed['first_time_owner'],
            'toleratesBeingAlone': breed['tolerates_being_alone'],
            'goodWithStrangers': breed['good_with_strangers'],
            'exerciseNeeds': breed['exercise_needs']
        }
        js_breeds.append(js_breed)
    
    # Write as JavaScript constant
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('const dogs = ')
        json.dump(js_breeds, f, indent=2, ensure_ascii=False)
        f.write(';\n')
    
    print(f"✅ Exported {len(js_breeds)} breeds to {output_file}\n")


if __name__ == '__main__':
    export_to_js()
