import json
import requests
import time

def normalize_size(size_text, weight_text=None):
    """Normalize size based on actual weight data, not arbitrary text parsing"""
    
    # If we have weight data, use that instead of text
    if weight_text:
        try:
            # Parse weight range like "20-30 lbs" or "55-75 lbs"
            weight_str = weight_text.lower().replace('lbs', '').replace('lb', '').strip()
            
            # Handle ranges
            if '-' in weight_str:
                parts = weight_str.split('-')
                # Use the max of the range as classification point
                max_weight = float(parts[1].strip())
            else:
                max_weight = float(weight_str)
            
            # Classify based on actual weight
            if max_weight < 25:
                return 'Small'
            elif max_weight < 60:
                return 'Medium'
            else:
                return 'Large'
        except:
            pass  # Fall back to text-based if weight parsing fails
    
    # Fallback to text-based classification (from original scrape data)
    size_lower = size_text.lower()
    if any(word in size_lower for word in ['toy', 'small']):
        return 'Small'
    elif any(word in size_lower for word in ['giant', 'extra-large']):
        return 'Large'
    elif 'large' in size_lower:
        return 'Large'
    else:
        return 'Medium'

def normalize_shedding(shedding):
    """Normalize shedding values to clear categories"""
    shedding_lower = shedding.lower()
    if 'minimal' in shedding_lower or 'hypoallergenic' in shedding_lower:
        return 'Non-Shedding'
    elif 'light' in shedding_lower or ('minimal' in shedding_lower and 'moderate' in shedding_lower):
        return 'Light Shedding'
    elif 'heavy' in shedding_lower:
        return 'Heavy Shedding'
    elif 'moderate' in shedding_lower:
        # Check if it's "Moderate to Heavy"
        if 'heavy' in shedding_lower:
            return 'Heavy Shedding'
        else:
            return 'Moderate Shedding'
    else:
        return 'Moderate Shedding'

def enrich_breed_photos(breed_name):
    """Get breed photos - hardcoded working Wikimedia Commons URLs"""
    print(f"  Using curated images...")
    
    # Hardcoded working Wikimedia Commons image URLs
    image_map = {
        'Golden Retriever': 'https://upload.wikimedia.org/wikipedia/commons/9/93/Golden_Retriever_Carlos_%2810581910556%29.jpg',
        'Labrador Retriever': 'https://upload.wikimedia.org/wikipedia/commons/3/34/Labrador_on_Quantock_%282175262184%29.jpg',
        'Cocker Spaniel': 'https://upload.wikimedia.org/wikipedia/commons/1/14/Cocker_spaniel_called_Tony.jpg',
        'English Springer Spaniel': 'https://upload.wikimedia.org/wikipedia/commons/d/db/English_Springer_Spaniel_in_Tallinn_1.jpg',
        'Irish Setter': 'https://upload.wikimedia.org/wikipedia/commons/f/f7/Irish_Setter_Justcharlies_Tanman_Takuna.jpg',
        'Beagle': 'https://upload.wikimedia.org/wikipedia/commons/b/b6/Shemsu_Sotis_Hera.jpg',
        'Bloodhound': 'https://upload.wikimedia.org/wikipedia/commons/3/38/Bloodhound_Puppy.jpg',
        'Dachshund': 'https://upload.wikimedia.org/wikipedia/commons/b/b9/Dachshund_brown_puppy.jpg',
        'Basset Hound': 'https://upload.wikimedia.org/wikipedia/commons/a/ae/BassetHound_profil.jpg',
        'Greyhound': 'https://upload.wikimedia.org/wikipedia/commons/1/1f/Greyhound_Racing_2_amk.jpg',
        'Siberian Husky': 'https://upload.wikimedia.org/wikipedia/commons/c/ca/Siberian-husky.jpg',
        'Boxer': 'https://upload.wikimedia.org/wikipedia/commons/6/6f/Male_fawn_Boxer_undocked.jpg',
        'Great Dane': 'https://upload.wikimedia.org/wikipedia/commons/f/f7/Great_Dane_Puppy.JPG',
        'Rottweiler': 'https://upload.wikimedia.org/wikipedia/commons/0/04/Rottweiler_kopf_2.jpg',
        'Bernese Mountain Dog': 'https://upload.wikimedia.org/wikipedia/commons/a/ab/Berner_Sennenhund.jpg',
        'Bull Terrier': 'https://upload.wikimedia.org/wikipedia/commons/d/de/Russian_Show_BT_Male.jpg',
        'Scottish Terrier': 'https://upload.wikimedia.org/wikipedia/commons/2/2e/Scottish_Terrier_Adult.jpg',
        'West Highland White Terrier': 'https://upload.wikimedia.org/wikipedia/commons/2/2c/West_Highland_White_Terrier_Krakow.jpg',
        'Yorkshire Terrier': 'https://upload.wikimedia.org/wikipedia/commons/4/4f/Yorkshire_Terrier_-_Hunde-16-08-2007-0009.jpg',
        'American Staffordshire Terrier': 'https://upload.wikimedia.org/wikipedia/commons/0/0f/Amerikansk_staffordshire_terrier_Rexlan_Pepsi.jpg',
        'Chihuahua': 'https://upload.wikimedia.org/wikipedia/commons/9/98/Chihuahua1_bvdb.jpg',
        'Pomeranian': 'https://upload.wikimedia.org/wikipedia/commons/3/35/Pomeranian_Dog.jpg',
        'Pug': 'https://upload.wikimedia.org/wikipedia/commons/f/f0/Mops_oct_2007.jpg',
        'Shih Tzu': 'https://upload.wikimedia.org/wikipedia/commons/4/42/Shih_Tzu_in_Tallinn_1.JPG',
        'Maltese': 'https://upload.wikimedia.org/wikipedia/commons/1/16/White_Maltese_dog.jpg',
        'French Bulldog': 'https://upload.wikimedia.org/wikipedia/commons/1/18/2008-07-28_Dog_at_Frolick_Field.jpg',
        'Poodle': 'https://upload.wikimedia.org/wikipedia/commons/3/35/Agility_Poodle.jpg',
        'Bulldog': 'https://upload.wikimedia.org/wikipedia/commons/1/16/English_bulldog_Ocobo_Audacious.jpg',
        'Boston Terrier': 'https://upload.wikimedia.org/wikipedia/commons/d/d7/Boston-terrier-carlos-de.JPG',
        'Dalmatian': 'https://upload.wikimedia.org/wikipedia/commons/8/8f/Dalmatiner_2.jpg',
        'German Shepherd': 'https://upload.wikimedia.org/wikipedia/commons/d/d0/German_Shepherd_-_DSC_0346_%2810096362833%29.jpg',
        'Border Collie': 'https://upload.wikimedia.org/wikipedia/commons/1/1f/Border_Collie_600.jpg',
        'Australian Shepherd': 'https://upload.wikimedia.org/wikipedia/commons/c/c4/Australian_Shepherd_600.jpg',
        'Pembroke Welsh Corgi': 'https://upload.wikimedia.org/wikipedia/commons/2/22/Welsh_Cardigan_Corgi-09-Albers.jpg',
        'Shetland Sheepdog': 'https://upload.wikimedia.org/wikipedia/commons/5/59/Shetland_Sheepdog_Sable.jpg',
    }
    
    url = image_map.get(breed_name)
    if url:
        print(f"    Using curated Wikimedia image")
        return [url]
    
    print(f"    No image available for {breed_name}")
    return []

def get_breed_characteristics(breed_name):
    """Get detailed breed characteristics from Dog CEO API and other sources"""
    print(f"  Getting detailed characteristics...")
    
    # This would ideally scrape from AKC, DogTime, or other breed databases
    # For now, returning structured placeholders that will be manually filled
    
    # Map breeds to realistic characteristics
    characteristics_db = {
        'Golden Retriever': {
            'size': 'Large',
            'weight': '55-75 lbs',
            'height': '21-24 inches',
            'energyLevel': 'High',
            'temperament': 'Friendly, intelligent, devoted, trustworthy',
            'goodWithKids': True,
            'goodWithPets': True,
            'groomingNeeds': 'Moderate - weekly brushing',
            'trainability': 'Very High',
            'shedding': 'Moderate to Heavy',
            'lifespan': '10-12 years',
            'origin': 'Scotland',
            'purpose': 'Sporting, Retriever',
            'barkingLevel': 'Moderate',
            'exerciseNeeds': '1-2 hours daily',
            'apartmentFriendly': 'With Exercise',
            'firstTimeOwner': 'Great',
            'toleratesBeingAlone': 'Moderate',
            'goodWithStrangers': 'Friendly'
        },
        'Labrador Retriever': {
            'size': 'Large',
            'weight': '55-80 lbs',
            'height': '21-24 inches',
            'energyLevel': 'Very High',
            'temperament': 'Friendly, active, outgoing, even-tempered',
            'goodWithKids': True,
            'goodWithPets': True,
            'groomingNeeds': 'Low - occasional brushing',
            'trainability': 'Very High',
            'shedding': 'Moderate',
            'lifespan': '10-12 years',
            'origin': 'Canada',
            'purpose': 'Sporting, Retriever',
            'barkingLevel': 'Moderate',
            'exerciseNeeds': '1-2 hours daily',
            'apartmentFriendly': 'With Exercise',
            'firstTimeOwner': 'Great',
            'toleratesBeingAlone': 'Moderate',
            'goodWithStrangers': 'Friendly'
        },
        'German Shepherd': {
            'size': 'Large',
            'weight': '50-90 lbs',
            'height': '22-26 inches',
            'energyLevel': 'High',
            'temperament': 'Confident, courageous, intelligent, loyal',
            'goodWithKids': True,
            'goodWithPets': 'With Socialization',
            'groomingNeeds': 'Moderate - regular brushing',
            'trainability': 'Very High',
            'shedding': 'Heavy',
            'lifespan': '9-13 years',
            'origin': 'Germany',
            'purpose': 'Herding, Working',
            'barkingLevel': 'Moderate to High',
            'exerciseNeeds': '1-2 hours daily',
            'apartmentFriendly': 'Not Recommended',
            'firstTimeOwner': 'Not Recommended',
            'toleratesBeingAlone': 'Moderate',
            'goodWithStrangers': 'Reserved'
        },
        'French Bulldog': {
            'size': 'Small',
            'weight': '16-28 lbs',
            'height': '11-13 inches',
            'energyLevel': 'Low to Moderate',
            'temperament': 'Playful, adaptable, smart, affectionate',
            'goodWithKids': True,
            'goodWithPets': True,
            'groomingNeeds': 'Low - minimal brushing',
            'trainability': 'Moderate',
            'shedding': 'Minimal',
            'lifespan': '10-12 years',
            'origin': 'France',
            'purpose': 'Companion',
            'barkingLevel': 'Low',
            'exerciseNeeds': '30 minutes daily',
            'apartmentFriendly': 'Yes',
            'firstTimeOwner': 'Great',
            'toleratesBeingAlone': 'Moderate',
            'goodWithStrangers': 'Friendly'
        },
        'Bulldog': {
            'size': 'Medium',
            'weight': '40-50 lbs',
            'height': '14-15 inches',
            'energyLevel': 'Low',
            'temperament': 'Friendly, calm, courageous, dignified',
            'goodWithKids': True,
            'goodWithPets': True,
            'groomingNeeds': 'Low - minimal brushing',
            'trainability': 'Moderate',
            'shedding': 'Moderate',
            'lifespan': '8-10 years',
            'origin': 'England',
            'purpose': 'Companion',
            'barkingLevel': 'Low',
            'exerciseNeeds': '30 minutes daily',
            'apartmentFriendly': 'Yes',
            'firstTimeOwner': 'Great',
            'toleratesBeingAlone': 'Yes',
            'goodWithStrangers': 'Friendly'
        },
        'Beagle': {
            'size': 'Medium',
            'weight': '20-30 lbs',
            'height': '13-15 inches',
            'energyLevel': 'High',
            'temperament': 'Friendly, curious, merry, determined',
            'goodWithKids': True,
            'goodWithPets': True,
            'groomingNeeds': 'Low - occasional brushing',
            'trainability': 'Moderate',
            'shedding': 'Moderate',
            'lifespan': '10-15 years',
            'origin': 'England',
            'purpose': 'Hound, Scent Tracking',
            'barkingLevel': 'High',
            'exerciseNeeds': '1 hour daily',
            'apartmentFriendly': 'With Exercise',
            'firstTimeOwner': 'Good',
            'toleratesBeingAlone': 'Not Recommended',
            'goodWithStrangers': 'Friendly'
        },
        'Poodle': {
            'size': 'Varies (Toy/Miniature/Standard)',
            'weight': '6-70 lbs',
            'height': '10-22 inches',
            'energyLevel': 'High',
            'temperament': 'Intelligent, active, alert, trainable',
            'goodWithKids': True,
            'goodWithPets': True,
            'groomingNeeds': 'High - regular professional grooming',
            'trainability': 'Very High',
            'shedding': 'Minimal (Hypoallergenic)',
            'lifespan': '12-15 years',
            'origin': 'Germany/France',
            'purpose': 'Companion, Water Retriever',
            'barkingLevel': 'Moderate',
            'exerciseNeeds': '1 hour daily',
            'apartmentFriendly': 'Yes',
            'firstTimeOwner': 'Great',
            'toleratesBeingAlone': 'Moderate',
            'goodWithStrangers': 'Friendly'
        },
        'Border Collie': {
            'size': 'Medium',
            'weight': '30-55 lbs',
            'height': '18-22 inches',
            'energyLevel': 'Very High',
            'temperament': 'Intelligent, energetic, responsive, alert',
            'goodWithKids': True,
            'goodWithPets': 'With Socialization',
            'groomingNeeds': 'Moderate - weekly brushing',
            'trainability': 'Very High',
            'shedding': 'Moderate',
            'lifespan': '12-15 years',
            'origin': 'Scotland/England Border',
            'purpose': 'Herding',
            'barkingLevel': 'Moderate to High',
            'exerciseNeeds': '2+ hours daily',
            'apartmentFriendly': 'Not Recommended',
            'firstTimeOwner': 'Not Recommended',
            'toleratesBeingAlone': 'Not Recommended',
            'goodWithStrangers': 'Reserved'
        },
        'Chihuahua': {
            'size': 'Toy',
            'weight': '2-6 lbs',
            'height': '5-8 inches',
            'energyLevel': 'Moderate',
            'temperament': 'Devoted, alert, quick, courageous',
            'goodWithKids': 'With Supervision',
            'goodWithPets': 'Selective',
            'groomingNeeds': 'Low - occasional brushing',
            'trainability': 'Moderate',
            'shedding': 'Minimal to Moderate',
            'lifespan': '14-16 years',
            'origin': 'Mexico',
            'purpose': 'Companion',
            'barkingLevel': 'High',
            'exerciseNeeds': '30 minutes daily',
            'apartmentFriendly': 'Yes',
            'firstTimeOwner': 'Good',
            'toleratesBeingAlone': 'Moderate',
            'goodWithStrangers': 'Reserved'
        },
        'Siberian Husky': {
            'size': 'Medium to Large',
            'weight': '35-60 lbs',
            'height': '20-24 inches',
            'energyLevel': 'Very High',
            'temperament': 'Outgoing, alert, friendly, independent',
            'goodWithKids': True,
            'goodWithPets': 'With Socialization',
            'groomingNeeds': 'Moderate - regular brushing',
            'trainability': 'Moderate',
            'shedding': 'Heavy',
            'lifespan': '12-14 years',
            'origin': 'Siberia',
            'purpose': 'Working, Sled Dog',
            'barkingLevel': 'Moderate',
            'exerciseNeeds': '2+ hours daily',
            'apartmentFriendly': 'Not Recommended',
            'firstTimeOwner': 'Not Recommended',
            'toleratesBeingAlone': 'Not Recommended',
            'goodWithStrangers': 'Friendly'
        }
    }
    
    # Return specific characteristics if available, otherwise generic placeholders
    if breed_name in characteristics_db:
        return characteristics_db[breed_name]
    else:
        return {
            'size': 'Medium',
            'weight': 'Varies',
            'height': 'Varies',
            'energyLevel': 'Moderate',
            'temperament': 'Friendly, intelligent, loyal',
            'goodWithKids': True,
            'goodWithPets': True,
            'groomingNeeds': 'Moderate',
            'trainability': 'Moderate',
            'shedding': 'Moderate',
            'lifespan': '10-13 years',
            'origin': 'Unknown',
            'purpose': 'Companion',
            'barkingLevel': 'Moderate',
            'exerciseNeeds': '1 hour daily',
            'apartmentFriendly': 'Yes',
            'firstTimeOwner': 'Good',
            'toleratesBeingAlone': 'Moderate',
            'goodWithStrangers': 'Friendly'
        }

def enrich_dog_database():
    """Enrich the dog breed database with photos and detailed information"""
    print("Enriching dog breed database...\n")
    
    # Load existing database
    with open('dog_breeds.json', 'r', encoding='utf-8') as f:
        breeds = json.load(f)
    
    enriched = []
    
    for i, breed in enumerate(breeds):
        print(f"[{i+1}/{len(breeds)}] {breed['name']}")
        
        # Get photos
        photos = enrich_breed_photos(breed['name'])
        
        # Get detailed characteristics
        characteristics = get_breed_characteristics(breed['name'])
        
        # Preserve original size if characteristics doesn't have real weight data
        original_size = breed.get('size', 'Medium')
        
        # Normalize size and shedding
        if 'size' in characteristics:
            weight = characteristics.get('weight', None)
            # Only use weight-based classification if we have real weight data
            if weight and weight != 'Varies':
                characteristics['size'] = normalize_size(characteristics['size'], weight)
            else:
                # Keep original size from scrape, but normalize the text
                characteristics['size'] = normalize_size(original_size, None)
        
        if 'shedding' in characteristics:
            characteristics['shedding'] = normalize_shedding(characteristics['shedding'])
        
        # Merge data
        breed.update(characteristics)
        
        # Update images - use Dog CEO photos if available, otherwise keep original
        if photos:
            breed['image'] = photos[0]  # Use first Dog CEO photo as main image
            breed['images'] = photos
        # If no photos from API, images array stays as is (from original scrape)
        
        enriched.append(breed)
        
        time.sleep(1)  # Rate limiting
    
    # Save enriched database
    with open('dog_breeds_enriched.json', 'w', encoding='utf-8') as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Enriched {len(enriched)} breeds")
    print("Saved to: dog_breeds_enriched.json")

if __name__ == '__main__':
    enrich_dog_database()
