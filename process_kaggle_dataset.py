"""
Process the Kaggle Dog Breeds Dataset
Source: https://www.kaggle.com/datasets/mexwell/dog-breeds-dataset
277 breeds from AKC with 21 columns of real data

Automatically downloads the dataset using kagglehub
"""
import csv
import json
import re
import os
import shutil

def download_dataset():
    """Download the Kaggle dataset using kagglehub"""
    print("Downloading dataset from Kaggle...\n")
    
    try:
        import kagglehub
        
        # Download latest version
        path = kagglehub.dataset_download("mexwell/dog-breeds-dataset")
        print(f"✅ Downloaded to: {path}\n")
        
        # Find the CSV file
        csv_files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.csv'):
                    csv_files.append(os.path.join(root, file))
        
        if not csv_files:
            print("❌ No CSV files found in downloaded dataset")
            return None
        
        # Use the first CSV file (should be akc-data-latest.csv)
        source_csv = csv_files[0]
        print(f"Found CSV: {os.path.basename(source_csv)}")
        
        # Copy to current directory
        dest_csv = 'akc-data-latest.csv'
        shutil.copy2(source_csv, dest_csv)
        print(f"Copied to: {dest_csv}\n")
        
        return dest_csv
        
    except ImportError:
        print("❌ kagglehub not installed")
        print("Install with: pip install kagglehub")
        print("\nOr manually download from:")
        print("https://www.kaggle.com/datasets/mexwell/dog-breeds-dataset")
        return None
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        print("\nTry manually downloading from:")
        print("https://www.kaggle.com/datasets/mexwell/dog-breeds-dataset")
        return None

def parse_weight(weight_str):
    """Parse weight string and return normalized value + size classification"""
    if not weight_str or weight_str.strip() == '':
        return None, None
    
    # Look for weight range like "55-75 pounds" or single values
    match = re.search(r'(\d+)-(\d+)\s*pounds?', weight_str, re.IGNORECASE)
    if match:
        min_w = int(match.group(1))
        max_w = int(match.group(2))
        
        # Classify based on max weight
        if max_w < 25:
            size = 'Small'
        elif max_w < 60:
            size = 'Medium'
        else:
            size = 'Large'
        
        return f"{min_w}-{max_w} lbs", size
    
    # Try single value
    match = re.search(r'(\d+)\s*pounds?', weight_str, re.IGNORECASE)
    if match:
        weight = int(match.group(1))
        if weight < 25:
            size = 'Small'
        elif weight < 60:
            size = 'Medium'
        else:
            size = 'Large'
        return f"{weight} lbs", size
    
    return weight_str.strip(), 'Medium'  # Default fallback

def parse_height(height_str):
    """Parse height string"""
    if not height_str or height_str.strip() == '':
        return None
    
    match = re.search(r'(\d+\.?\d*)-(\d+\.?\d*)\s*inches?', height_str, re.IGNORECASE)
    if match:
        return f"{match.group(1)}-{match.group(2)} inches"
    
    match = re.search(r'(\d+\.?\d*)\s*inches?', height_str, re.IGNORECASE)
    if match:
        return f"{match.group(1)} inches"
    
    return height_str.strip()

def normalize_group(group_str):
    """Normalize group names"""
    if not group_str:
        return 'miscellaneous', 'Miscellaneous'
    
    group_lower = group_str.lower()
    
    group_map = {
        'sporting': ('sporting', 'Sporting Group'),
        'hound': ('hound', 'Hound Group'),
        'working': ('working', 'Working Group'),
        'terrier': ('terrier', 'Terrier Group'),
        'toy': ('toy', 'Toy Group'),
        'non-sporting': ('non-sporting', 'Non-Sporting Group'),
        'herding': ('herding', 'Herding Group'),
        'miscellaneous': ('miscellaneous', 'Miscellaneous Class'),
    }
    
    for key, (slug, display) in group_map.items():
        if key in group_lower:
            return slug, display
    
    return 'miscellaneous', 'Miscellaneous'

def normalize_shedding(shedding_cat):
    """Normalize shedding categories from CSV"""
    if not shedding_cat:
        return 'Moderate Shedding'
    
    shedding_lower = shedding_cat.lower()
    
    if 'infrequent' in shedding_lower:
        return 'Non-Shedding'
    elif any(word in shedding_lower for word in ['frequent', 'regularly']):
        return 'Heavy Shedding'
    else:
        return 'Moderate Shedding'

def process_csv_to_json(csv_file):
    """Convert Kaggle CSV to our JSON format"""
    print(f"Reading {csv_file}...\n")
    
    breeds = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Print column names to see what we're working with
        print("CSV Columns:")
        for i, col in enumerate(reader.fieldnames, 1):
            print(f"  {i}. {col}")
        print()
        
        for i, row in enumerate(reader, 1):
            # Get breed name from first column (which is unnamed in the CSV)
            breed_name = row.get('') or row.get('name') or row.get('breed_name') or f'Breed {i}'
            
            # Construct weight range from min and max columns (CSV is in kg, convert to lbs)
            min_w = row.get('min_weight', '').strip()
            max_w = row.get('max_weight', '').strip()
            
            if min_w and max_w:
                try:
                    min_weight_kg = float(min_w)
                    max_weight_kg = float(max_w)
                    # Convert kg to lbs (1 kg = 2.20462 lbs)
                    min_weight_lbs = min_weight_kg * 2.20462
                    max_weight_lbs = max_weight_kg * 2.20462
                    weight = f"{int(min_weight_lbs)}-{int(max_weight_lbs)} lbs"
                    
                    # Classify size based on max weight in lbs
                    if max_weight_lbs < 25:
                        size = 'Small'
                    elif max_weight_lbs < 60:
                        size = 'Medium'
                    else:
                        size = 'Large'
                except:
                    weight = 'Varies'
                    size = 'Medium'
            else:
                weight = 'Varies'
                size = 'Medium'
            
            # Construct height range from min and max columns (CSV is in cm, convert to inches)
            min_h = row.get('min_height', '').strip()
            max_h = row.get('max_height', '').strip()
            
            if min_h and max_h:
                try:
                    min_height_cm = float(min_h)
                    max_height_cm = float(max_h)
                    # Convert cm to inches (1 inch = 2.54 cm)
                    min_height_in = min_height_cm / 2.54
                    max_height_in = max_height_cm / 2.54
                    height = f"{int(min_height_in)}-{int(max_height_in)} inches"
                except:
                    height = 'Varies'
            else:
                height = 'Varies'
            
            # Construct lifespan from min and max expectancy
            min_exp = row.get('min_expectancy', '').strip()
            max_exp = row.get('max_expectancy', '').strip()
            
            if min_exp and max_exp:
                lifespan = f"{min_exp}-{max_exp} years"
            else:
                lifespan = '10-13 years'
            
            # Parse group
            group, group_display = normalize_group(row.get('group') or '')
            
            # Create breed object
            breed = {
                'id': i,
                'name': breed_name,
                'group': group,
                'groupDisplay': group_display,
                'size': size,
                'weight': weight,
                'height': height,
                'lifespan': lifespan,
                'temperament': (row.get('temperament') or 'Friendly, loyal').strip(),
                'energyLevel': (row.get('energy_level_value') or row.get('energy') or 'Moderate').strip(),
                'trainability': (row.get('trainability_value') or row.get('trainability') or 'Moderate').strip(),
                'shedding': normalize_shedding(row.get('shedding_category') or ''),
                'groomingNeeds': (row.get('grooming_frequency_value') or row.get('grooming') or 'Moderate').strip(),
                'goodWithKids': row.get('demeanor_category', '').lower() in ['friendly', 'outgoing'],
                'goodWithPets': row.get('demeanor_category', '').lower() in ['friendly', 'outgoing'],
                'barkingLevel': (row.get('barking_level_value') or row.get('barking') or 'Moderate').strip(),
                'origin': 'United States',  # Placeholder
                'image': f"https://via.placeholder.com/400x400.png?text={breed_name.replace(' ', '+')}",
                'images': [],
                'wikipediaUrl': None,
                # User-focused fields
                'apartmentFriendly': 'Unknown',
                'firstTimeOwner': 'Good',
                'toleratesBeingAlone': 'Moderate',
                'goodWithStrangers': 'Friendly',
                'exerciseNeeds': '1 hour daily',
            }
            
            breeds.append(breed)
            
            if i % 50 == 0:
                print(f"  Processed {i} breeds...")
    
    print(f"\n✅ Processed {len(breeds)} breeds from Kaggle dataset")
    return breeds

def main():
    csv_file = 'akc-data-latest.csv'
    
    # Check if file exists, if not try to download
    if not os.path.exists(csv_file):
        print(f"📥 {csv_file} not found locally, attempting download...\n")
        csv_file = download_dataset()
        
        if not csv_file:
            print("\n❌ Could not download dataset")
            print("\nManual steps:")
            print("1. Go to: https://www.kaggle.com/datasets/mexwell/dog-breeds-dataset")
            print("2. Download 'akc-data-latest.csv'")
            print("3. Place it in the dog-breeds folder")
            print("4. Run this script again")
            return
    else:
        print(f"✅ Found {csv_file}\n")
    
    # Process CSV
    breeds = process_csv_to_json(csv_file)
    
    # Save to JSON
    output_file = 'dog_breeds_kaggle.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(breeds, f, indent=2)
    
    print(f"\n💾 Saved to: {output_file}")
    
    # Show statistics
    size_counts = {}
    group_counts = {}
    
    for breed in breeds:
        size_counts[breed['size']] = size_counts.get(breed['size'], 0) + 1
        group_counts[breed['group']] = group_counts.get(breed['group'], 0) + 1
    
    print("\n📊 Statistics:")
    print(f"  Total breeds: {len(breeds)}")
    print("\n  By Size:")
    for size, count in sorted(size_counts.items()):
        print(f"    {size}: {count}")
    print("\n  By Group:")
    for group, count in sorted(group_counts.items()):
        print(f"    {group}: {count}")

if __name__ == '__main__':
    main()
