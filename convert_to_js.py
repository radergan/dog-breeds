import json

def convert_to_js():
    """Convert dog_breeds_kaggle.json to JavaScript format"""
    
    with open('dog_breeds_kaggle.json', 'r', encoding='utf-8') as f:
        breeds = json.load(f)
    
    with open('dogs.js', 'w', encoding='utf-8') as f:
        f.write('const dogs = [\n')
        
        for i, breed in enumerate(breeds):
            f.write('  {\n')
            f.write(f'    id: {breed["id"]},\n')
            f.write(f'    name: "{breed["name"]}",\n')
            f.write(f'    group: "{breed["group"]}",\n')
            f.write(f'    groupDisplay: "{breed["groupDisplay"]}",\n')
            f.write(f'    size: "{breed["size"]}",\n')
            f.write(f'    energyLevel: "{breed["energyLevel"]}",\n')
            f.write(f'    temperament: "{breed["temperament"]}",\n')
            
            # Handle goodWithKids which might be string or boolean
            if isinstance(breed["goodWithKids"], bool):
                f.write(f'    goodWithKids: {str(breed["goodWithKids"]).lower()},\n')
            else:
                f.write(f'    goodWithKids: "{breed["goodWithKids"]}",\n')
            
            # Handle goodWithPets which might be string or boolean
            if isinstance(breed["goodWithPets"], bool):
                f.write(f'    goodWithPets: {str(breed["goodWithPets"]).lower()},\n')
            else:
                f.write(f'    goodWithPets: "{breed["goodWithPets"]}",\n')
            
            f.write(f'    groomingNeeds: "{breed["groomingNeeds"]}",\n')
            f.write(f'    trainability: "{breed["trainability"]}",\n')
            f.write(f'    shedding: "{breed["shedding"]}",\n')
            f.write(f'    lifespan: "{breed["lifespan"]}",\n')
            f.write(f'    image: "{breed["image"]}",\n')
            
            # Handle images array
            if breed.get('images'):
                images_json = json.dumps(breed['images'])
                f.write(f'    images: {images_json},\n')
            else:
                f.write(f'    images: ["{breed["image"]}"],\n')
            
            # Handle optional fields
            if breed.get('wikipediaUrl'):
                f.write(f'    wikipediaUrl: "{breed["wikipediaUrl"]}",\n')
            else:
                f.write(f'    wikipediaUrl: null,\n')
            
            if breed.get('origin'):
                f.write(f'    origin: "{breed["origin"]}",\n')
            
            if breed.get('weight'):
                f.write(f'    weight: "{breed["weight"]}",\n')
            
            if breed.get('height'):
                f.write(f'    height: "{breed["height"]}",\n')
            
            if breed.get('purpose'):
                f.write(f'    purpose: "{breed["purpose"]}",\n')
            
            if breed.get('barkingLevel'):
                f.write(f'    barkingLevel: "{breed["barkingLevel"]}",\n')
            
            if breed.get('exerciseNeeds'):
                f.write(f'    exerciseNeeds: "{breed["exerciseNeeds"]}",\n')
            
            # New user-focused fields
            if breed.get('apartmentFriendly'):
                f.write(f'    apartmentFriendly: "{breed["apartmentFriendly"]}",\n')
            
            if breed.get('firstTimeOwner'):
                f.write(f'    firstTimeOwner: "{breed["firstTimeOwner"]}",\n')
            
            if breed.get('toleratesBeingAlone'):
                f.write(f'    toleratesBeingAlone: "{breed["toleratesBeingAlone"]}",\n')
            
            if breed.get('goodWithStrangers'):
                f.write(f'    goodWithStrangers: "{breed["goodWithStrangers"]}",\n')
            
            if i < len(breeds) - 1:
                f.write('  },\n')
            else:
                f.write('  }\n')
        
        f.write('];\n')
    
    print(f"✅ Converted {len(breeds)} breeds to dogs.js")

if __name__ == '__main__':
    convert_to_js()
