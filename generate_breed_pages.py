import json
import os

def create_slug(name):
    """Create URL-friendly slug from breed name"""
    return name.lower().replace(' ', '-').replace("'", '')

def generate_breed_page(breed, template):
    """Generate individual HTML page for a breed"""
    
    # Create slug for filename
    slug = create_slug(breed['name'])
    
    # Helper function to check if value is useful
    def is_useful(value):
        if not value:
            return False
        useless_values = ['varies', 'unknown', 'n/a', 'not available']
        return str(value).lower().strip() not in useless_values
    
    # Handle boolean/string values
    kids_friendly = 'Yes' if breed['goodWithKids'] == True else ('No' if breed['goodWithKids'] == False else breed['goodWithKids'])
    pets_friendly = 'Yes' if breed['goodWithPets'] == True else ('No' if breed['goodWithPets'] == False else breed['goodWithPets'])
    
    # Build image gallery HTML
    images_html = ''
    if breed.get('images') and len(breed['images']) > 1:
        for idx, img_url in enumerate(breed['images']):
            active = 'active' if idx == 0 else ''
            images_html += f'<img src="{img_url}" alt="{breed["name"]} photo {idx+1}" class="breed-image {active}" id="image-{idx}">\n                '
        
        # Add navigation if multiple images
        nav_html = f'''
                <div class="image-nav">
                    <button class="nav-btn prev" onclick="changeImage(-1)">‹</button>
                    <span class="image-indicator" id="image-indicator">1 of {len(breed['images'])}</span>
                    <button class="nav-btn next" onclick="changeImage(1)">›</button>
                </div>'''
    else:
        images_html = f'<img src="{breed["image"]}" alt="{breed["name"]}" class="breed-image active">'
        nav_html = ''
    
    # Build Size & Physical Traits section with only useful data
    size_items = []
    size_items.append(f'<div class="info-item"><div class="info-label">Size</div><div class="info-value">{breed["size"]}</div></div>')
    
    weight = breed.get('weight', '')
    if is_useful(weight):
        size_items.append(f'<div class="info-item"><div class="info-label">Weight</div><div class="info-value">{weight}</div></div>')
    
    height = breed.get('height', '')
    if is_useful(height):
        size_items.append(f'<div class="info-item"><div class="info-label">Height</div><div class="info-value">{height}</div></div>')
    
    size_items.append(f'<div class="info-item"><div class="info-label">Lifespan</div><div class="info-value">{breed["lifespan"]}</div></div>')
    size_physical_html = '\n                                '.join(size_items)
    
    # Build Background section with only useful data
    background_items = []
    origin = breed.get('origin', '')
    if is_useful(origin):
        background_items.append(f'<div class="info-item"><div class="info-label">Origin</div><div class="info-value">{origin}</div></div>')
    
    purpose = breed.get('purpose', '')
    if is_useful(purpose):
        background_items.append(f'<div class="info-item"><div class="info-label">Original Purpose</div><div class="info-value">{purpose}</div></div>')
    
    # Only include Background section if we have useful data
    wiki_link = f'<a href="{breed["wikipediaUrl"]}" target="_blank" class="wiki-link">Read more on Wikipedia →</a>' if breed.get('wikipediaUrl') else ''
    
    if background_items or wiki_link:
        background_grid_html = '\n                                '.join(background_items) if background_items else ''
        background_section = f'''<div class="info-section">
                        <h2>Background</h2>
                        <div class="info-grid">
                            {background_grid_html}
                        </div>
                        {wiki_link}
                    </div>'''
    else:
        background_section = ''
    
    # Replace placeholders in template
    html = template.replace('{{BREED_NAME}}', breed['name'])
    html = html.replace('{{BREED_SLUG}}', slug)
    html = html.replace('{{GROUP_DISPLAY}}', breed['groupDisplay'])
    html = html.replace('{{SIZE_PHYSICAL_HTML}}', size_physical_html)
    html = html.replace('{{TEMPERAMENT}}', breed['temperament'])
    html = html.replace('{{ENERGY_LEVEL}}', breed['energyLevel'])
    html = html.replace('{{EXERCISE_NEEDS}}', breed.get('exerciseNeeds', 'Moderate exercise'))
    html = html.replace('{{APARTMENT_FRIENDLY}}', breed.get('apartmentFriendly', 'Unknown'))
    html = html.replace('{{KIDS_FRIENDLY}}', kids_friendly)
    html = html.replace('{{PETS_FRIENDLY}}', pets_friendly)
    html = html.replace('{{STRANGERS}}', breed.get('goodWithStrangers', 'Unknown'))
    html = html.replace('{{ALONE_TIME}}', breed.get('toleratesBeingAlone', 'Unknown'))
    html = html.replace('{{FIRST_TIME_OWNER}}', breed.get('firstTimeOwner', 'Unknown'))
    html = html.replace('{{GROOMING}}', breed['groomingNeeds'])
    html = html.replace('{{SHEDDING}}', breed['shedding'])
    html = html.replace('{{TRAINABILITY}}', breed['trainability'])
    html = html.replace('{{BARKING}}', breed.get('barkingLevel', 'Unknown'))
    html = html.replace('{{BACKGROUND_SECTION}}', background_section)
    html = html.replace('{{IMAGES_HTML}}', images_html)
    html = html.replace('{{IMAGE_NAV_HTML}}', nav_html)
    html = html.replace('{{MAIN_IMAGE}}', breed['image'])
    
    return slug, html

def load_template():
    """Load the breed page template from index.html"""
    # Read index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Get everything before preview-section (line 646 in 1-indexed = index 645 in 0-indexed, so use [0:645])
    header_section = ''.join(lines[0:645])
    
    # Get everything after preview-section closes (lines 659-754, but in 0-indexed that's 658-753)
    footer_section = ''.join(lines[658:])
    
    # Remove breadcrumbs from breed pages
    breadcrumb_start = header_section.find('<div class="breadcrumb-search-container">')
    breadcrumb_end = header_section.find('</div>', breadcrumb_start) + len('</div>')
    if breadcrumb_start != -1 and breadcrumb_end != -1:
        # Find the next newline after </div> to keep formatting clean
        next_newline = header_section.find('\n', breadcrumb_end)
        if next_newline != -1:
            breadcrumb_end = next_newline + 1
        header_section = header_section[:breadcrumb_start] + header_section[breadcrumb_end:]
    
    # Build the breed-specific preview-section content
    breed_content = '''
        <div class="preview-section show" id="preview-section">
            <div class="breed-header">
                <h1 class="breed-title">{{BREED_NAME}}</h1>
                <p class="breed-subtitle">{{GROUP_DISPLAY}}</p>
            </div>
            
            <div class="breed-content">
                <div class="breed-images">
                    <div class="image-container">
                        {{IMAGES_HTML}}
                    </div>
                    {{IMAGE_NAV_HTML}}
                </div>
                
                <div class="breed-info">
                    <div class="info-section">
                        <h2>Size & Physical Traits</h2>
                        <div class="info-grid">
                            {{SIZE_PHYSICAL_HTML}}
                        </div>
                    </div>
                    
                    <div class="info-section">
                        <h2>Temperament</h2>
                        <div class="temperament-box">
                            {{TEMPERAMENT}}
                        </div>
                    </div>
                    
                    <div class="info-section">
                        <h2>Living Situation</h2>
                        <div class="info-grid">
                            <div class="info-item">
                                <div class="info-label">Apartment Friendly</div>
                                <div class="info-value">{{APARTMENT_FRIENDLY}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">First-Time Owner</div>
                                <div class="info-value">{{FIRST_TIME_OWNER}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Can Be Left Alone</div>
                                <div class="info-value">{{ALONE_TIME}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Energy Level</div>
                                <div class="info-value">{{ENERGY_LEVEL}}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="info-section">
                        <h2>Family & Social</h2>
                        <div class="info-grid">
                            <div class="info-item">
                                <div class="info-label">Good with Kids</div>
                                <div class="info-value">{{KIDS_FRIENDLY}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Good with Pets</div>
                                <div class="info-value">{{PETS_FRIENDLY}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">With Strangers</div>
                                <div class="info-value">{{STRANGERS}}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="info-section">
                        <h2>Care & Training</h2>
                        <div class="info-grid">
                            <div class="info-item">
                                <div class="info-label">Exercise Needs</div>
                                <div class="info-value">{{EXERCISE_NEEDS}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Grooming</div>
                                <div class="info-value">{{GROOMING}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Shedding</div>
                                <div class="info-value">{{SHEDDING}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Trainability</div>
                                <div class="info-value">{{TRAINABILITY}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Barking Level</div>
                                <div class="info-value">{{BARKING}}</div>
                            </div>
                        </div>
                    </div>
                    
                    {{BACKGROUND_SECTION}}
                </div>
            </div>
        </div>
        '''
    
    # Combine: header + breed content + footer
    # Also update meta tags and title in header section
    header_section = header_section.replace(
        '<title>Dog Breed Finder - Complete Database of Dog Breeds</title>',
        '<title>{{BREED_NAME}} - Dog Breed Finder</title>'
    )
    header_section = header_section.replace(
        '<meta name="description" content="Comprehensive database of dog breeds. Browse by size, shedding level, and AKC group. Find the perfect breed for your family.">',
        '<meta name="description" content="Learn about the {{BREED_NAME}}: temperament, size, exercise needs, and more. {{TEMPERAMENT}}">'
    )
    # Fix links to go back to parent directory
    header_section = header_section.replace('href="index.html"', 'href="../index.html"')
    
    # Replace the sidebar content with simple back link
    sidebar_start = header_section.find('<aside class="sidebar">')
    sidebar_end = header_section.find('</aside>') + len('</aside>')
    if sidebar_start != -1 and sidebar_end != -1:
        new_sidebar = '''<aside class="sidebar">
            <div class="side-nav">
                <div class="accordion">
                    <input type="checkbox" id="accordion-0" name="accordion-checkbox" checked>
                    <label class="accordion-header" for="accordion-0">Quick Links</label>
                    <div class="accordion-body">
                        <a href="../index.html" style="text-decoration: none;">
                            <div class="subfamily-item">
                                <div class="subfamily-name">← Back to Browse</div>
                                <div class="subfamily-desc">View all breeds</div>
                            </div>
                        </a>
                    </div>
                </div>
            </div>
        </aside>'''
        header_section = header_section[:sidebar_start] + new_sidebar + header_section[sidebar_end:]
    
    # Add breed-specific CSS before </style>
    breed_css = '''
        .breed-header {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .breed-title {
            font-size: 1.875rem;
            font-weight: 600;
            color: #2d3748;
            margin: 0 0 0.5rem 0;
        }
        
        .breed-subtitle {
            font-size: 1rem;
            color: #718096;
            margin: 0;
        }
        
        .breed-content {
            display: grid;
            grid-template-columns: 400px 1fr;
            gap: 40px;
        }
        
        .breed-images {
            background: #f7f8f9;
            border-radius: 8px;
            overflow: hidden;
            position: relative;
        }
        
        .image-container {
            position: relative;
            width: 100%;
            padding-top: 100%;
            background: #e8e6e3;
        }
        
        .breed-image {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: none;
        }
        
        .breed-image.active {
            display: block;
        }
        
        .image-nav {
            position: absolute;
            bottom: 1rem;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            gap: 1rem;
            background: rgba(0,0,0,0.7);
            padding: 0.5rem 1rem;
            border-radius: 20px;
        }
        
        .nav-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.25rem;
            cursor: pointer;
            padding: 0 0.5rem;
        }
        
        .nav-btn:hover {
            opacity: 0.8;
        }
        
        .image-indicator {
            color: white;
            font-size: 0.875rem;
        }
        
        .breed-info {
        }
        
        .info-section {
            margin-bottom: 2rem;
        }
        
        .info-section:last-child {
            margin-bottom: 0;
        }
        
        .info-section h2 {
            font-size: 1.125rem;
            font-weight: 600;
            color: #2d3748;
            margin: 0 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #5755d9;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }
        
        .info-item {
            padding: 0.75rem;
            background: #f7f8f9;
            border-radius: 6px;
        }
        
        .info-label {
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 0.25rem;
        }
        
        .info-value {
            color: #2d3748;
        }
        
        .temperament-box {
            background: #f7fafc;
            padding: 1rem;
            border-radius: 6px;
            border-left: 4px solid #5755d9;
        }
        
        .wiki-link {
            display: inline-block;
            margin-top: 1rem;
            color: #5755d9;
            text-decoration: none;
            font-weight: 500;
        }
        
        .wiki-link:hover {
            text-decoration: underline;
        }
        
        @media (max-width: 968px) {
            .breed-content {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 768px) {
            .info-grid {
                grid-template-columns: 1fr;
            }
            .breed-title {
                font-size: 1.5rem;
            }
        }
    '''
    header_section = header_section.replace('</style>', breed_css + '\n    </style>')
    
    # Add gallery navigation script before </body>
    footer_section = footer_section.replace(
        '<script src="dogs.js"></script>',
        '''<script>
        let currentImageIndex = 0;
        const images = document.querySelectorAll('.breed-image');
        const totalImages = images.length;
        
        function changeImage(direction) {
            if (totalImages <= 1) return;
            
            images[currentImageIndex].classList.remove('active');
            currentImageIndex = (currentImageIndex + direction + totalImages) % totalImages;
            images[currentImageIndex].classList.add('active');
            
            document.getElementById('image-indicator').textContent = `${currentImageIndex + 1} of ${totalImages}`;
        }
    </script>'''
    )
    footer_section = footer_section.replace('<script src="app.js"></script>', '')
    
    template = header_section + breed_content + footer_section
    return template

def main():
    """Generate all breed pages"""
    # Load Kaggle breeds data
    with open('dog_breeds_kaggle.json', 'r', encoding='utf-8') as f:
        breeds = json.load(f)
    
    # Create breeds directory
    os.makedirs('breeds', exist_ok=True)
    
    # Load template
    template = load_template()
    
    # Generate page for each breed
    for breed in breeds:
        slug, html = generate_breed_page(breed, template)
        
        # Write to file
        filepath = os.path.join('breeds', f'{slug}.html')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Generated: breeds/{slug}.html")
    
    print(f"\n🎉 Generated {len(breeds)} breed pages in /breeds/")

if __name__ == '__main__':
    main()
