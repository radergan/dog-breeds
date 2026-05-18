"""
Scrape REAL dog breed data from the American Kennel Club website
Step 1: Get the official AKC breed list
Step 2: Scrape each breed's actual data
Instead of making shit up with arbitrary lists
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re

def get_akc_breed_list():
    """Scrape the official AKC breed directory to get ALL breeds"""
    print("Fetching official AKC breed list...\n")
    
    breeds = []
    page = 1
    max_pages = 20  # Safety limit, AKC has ~200 breeds so probably ~10-15 pages
    
    while page <= max_pages:
        url = f"https://www.akc.org/dog-breeds/page/{page}/" if page > 1 else "https://www.akc.org/dog-breeds/"
        print(f"  Page {page}: {url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all breed links - they're in <a> tags with href="/dog-breeds/breed-name/"
            breed_links = soup.find_all('a', href=re.compile(r'^https://www\.akc\.org/dog-breeds/[^/]+/$'))
            
            if not breed_links:
                print(f"  No more breeds found on page {page}")
                break
            
            for link in breed_links:
                breed_name = link.get_text().strip()
                breed_url = link['href']
                
                if breed_name and breed_url:
                    # Extract slug from URL
                    slug = breed_url.rstrip('/').split('/')[-1]
                    breeds.append({
                        'name': breed_name,
                        'slug': slug,
                        'url': breed_url
                    })
            
            print(f"    Found {len(breed_links)} breeds on this page (total: {len(breeds)})")
            
            # Check if there's a "next page" button
            load_more = soup.find('a', string=re.compile('LOAD MORE', re.IGNORECASE))
            if not load_more:
                print(f"  Reached last page")
                break
            
            page += 1
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"  Error on page {page}: {e}")
            break
    
    # Deduplicate by breed name
    unique_breeds = {}
    for breed in breeds:
        if breed['name'] not in unique_breeds:
            unique_breeds[breed['name']] = breed
    
    breed_list = list(unique_breeds.values())
    breed_list.sort(key=lambda x: x['name'])
    
    print(f"\n✅ Found {len(breed_list)} official AKC breeds\n")
    return breed_list

def parse_weight(weight_text):
    """Extract weight range from AKC format like '65-75 pounds (male)'"""
    match = re.search(r'(\d+)-(\d+)\s*pounds?', weight_text.lower())
    if match:
        return f"{match.group(1)}-{match.group(2)} lbs"
    return weight_text.strip()

def parse_height(height_text):
    """Extract height range from AKC format like '23-24 inches (male)'"""
    match = re.search(r'(\d+\.?\d*)-(\d+\.?\d*)\s*inches?', height_text.lower())
    if match:
        return f"{match.group(1)}-{match.group(2)} inches"
    return height_text.strip()

def scrape_breed_data(breed_info):
    """Scrape individual breed page from AKC"""
    url = breed_info['url']
    breed_name = breed_info['name']
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            'name': breed_name,
            'akc_url': url
        }
        
        # Extract weight
        weight_section = soup.find('h3', string=re.compile('WEIGHT', re.IGNORECASE))
        if weight_section:
            weight_text = weight_section.find_next_sibling(string=True)
            if weight_text:
                data['weight'] = parse_weight(weight_text)
        
        # Extract height
        height_section = soup.find('h3', string=re.compile('HEIGHT', re.IGNORECASE))
        if height_section:
            height_text = height_section.find_next_sibling(string=True)
            if height_text:
                data['height'] = parse_height(height_text)
        
        # Extract life expectancy
        life_section = soup.find('h3', string=re.compile('LIFE EXPECTANCY', re.IGNORECASE))
        if life_section:
            life_text = life_section.find_next_sibling(string=True)
            if life_text:
                data['lifespan'] = life_text.strip()
        
        # Extract group
        group_link = soup.find('a', href=re.compile(r'/dog-breeds/(sporting|hound|working|terrier|toy|non-sporting|herding)/'))
        if group_link:
            data['group'] = group_link.get_text().strip()
        
        # Get the "About the Breed" description
        about_section = soup.find('h2', string=re.compile('About the Breed', re.IGNORECASE))
        if about_section:
            about_p = about_section.find_next('p')
            if about_p:
                data['description'] = about_p.get_text().strip()[:500]  # First 500 chars
        
        return data
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def main():
    """Scrape all breeds from AKC"""
    
    # Step 1: Get official breed list from AKC
    breed_list = get_akc_breed_list()
    
    # Save breed list
    with open('akc_breed_list.json', 'w', encoding='utf-8') as f:
        json.dump(breed_list, f, indent=2)
    print(f"Saved breed list to: akc_breed_list.json\n")
    
    # Step 2: Scrape data for each breed
    print(f"Now scraping data for {len(breed_list)} breeds...\n")
    
    results = []
    
    for i, breed_info in enumerate(breed_list):
        print(f"[{i+1}/{len(breed_list)}] {breed_info['name']}")
        data = scrape_breed_data(breed_info)
        
        if data:
            results.append(data)
            print(f"  ✅ weight={data.get('weight', 'N/A')}, height={data.get('height', 'N/A')}, group={data.get('group', 'N/A')}")
        
        # Rate limiting - be respectful to AKC servers
        if i < len(breed_list) - 1:
            time.sleep(2)
    
    # Save results
    output_file = 'akc_scraped_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Scraped {len(results)}/{len(breed_list)} breeds")
    print(f"Saved to: {output_file}")
    
    # Show summary
    have_weight = sum(1 for r in results if 'weight' in r)
    have_height = sum(1 for r in results if 'height' in r)
    have_group = sum(1 for r in results if 'group' in r)
    print(f"\nData coverage:")
    print(f"  Weight: {have_weight}/{len(results)}")
    print(f"  Height: {have_height}/{len(results)}")
    print(f"  Group: {have_group}/{len(results)}")

if __name__ == '__main__':
    main()
