import json
import os
import breed_db

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
    kids_value = breed.get('goodWithKids')
    kids_friendly = 'Yes' if kids_value == True or kids_value == 1 else ('No' if kids_value == False or kids_value == 0 else 'Unknown')
    
    pets_value = breed.get('goodWithPets')
    pets_friendly = 'Yes' if pets_value == True or pets_value == 1 else ('No' if pets_value == False or pets_value == 0 else 'Unknown')
    
    # Build image gallery HTML
    images_html = ''
    main_image = breed.get('image', f'https://via.placeholder.com/400x400.png?text={breed["name"].replace(" ", "+")}')
    additional_images = breed.get('images', [])
    
    # Combine main image with additional images
    all_images = [main_image]
    if additional_images:
        all_images.extend(additional_images)
    
    if len(all_images) > 1:
        # Multiple images - create gallery with navigation
        for idx, img_url in enumerate(all_images):
            active = 'active' if idx == 0 else ''
            images_html += f'<img src="{img_url}" alt="{breed["name"]} photo {idx+1}" class="breed-image {active}" id="image-{idx}">\n                '
        
        # Add navigation
        nav_html = f'''
                <div class="image-nav">
                    <button class="nav-btn prev" onclick="changeImage(-1)">‹</button>
                    <span class="image-indicator" id="image-indicator">1 of {len(all_images)}</span>
                    <button class="nav-btn next" onclick="changeImage(1)">›</button>
                </div>'''
    else:
        # Single image only
        images_html = f'<img src="{main_image}" alt="{breed["name"]}" class="breed-image active">'
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
    
    # Generate temperament chips
    temperament_traits = [trait.strip() for trait in breed['temperament'].split(',')]
    temperament_chips = '\n                    '.join([f'<span class="chip">{trait}</span>' for trait in temperament_traits])
    
    # Build summary section with gallery
    summary = breed.get('summary')
    if summary and summary.strip():
        summary_section = f'''<div class="breed-summary">
                    <div class="summary-text">
                        <h2>About the {breed['name']}</h2>
                        <p>{summary}</p>
                    </div>
                    <div class="breed-images">
                        <div class="image-container">
                            {images_html}
                        </div>
                        {nav_html}
                    </div>
                </div>'''
    else:
        # No summary, just show gallery
        summary_section = f'''<div class="breed-images-only">
                    <div class="image-container">
                        {images_html}
                    </div>
                    {nav_html}
                </div>'''
    
    # Convert boolean fields to Yes/No
    apartment_friendly = 'Yes' if breed.get('apartmentFriendly') == True else ('No' if breed.get('apartmentFriendly') == False else 'Unknown')
    strangers = 'Yes' if breed.get('goodWithStrangers') == True else ('No' if breed.get('goodWithStrangers') == False else 'Unknown')
    alone_time = 'Yes' if breed.get('toleratesBeingAlone') == True else ('No' if breed.get('toleratesBeingAlone') == False else 'Unknown')
    first_time = 'Yes' if breed.get('firstTimeOwner') == True else ('No' if breed.get('firstTimeOwner') == False else 'Unknown')
    
    # Convert grooming and trainability to progress bars
    def make_progress_bar(value_str):
        try:
            value = float(value_str)
            percentage = int(value * 100)
            return f'<div class="bar"><div class="bar-item" role="progressbar" style="width:{percentage}%;" aria-valuenow="{percentage}" aria-valuemin="0" aria-valuemax="100"></div></div>'
        except:
            return value_str
    
    grooming_bar = make_progress_bar(breed['groomingNeeds'])
    trainability_bar = make_progress_bar(breed['trainability'])
    
    # Prepare social sharing metadata
    summary = breed.get('summary')
    summary_preview = summary[:150] + '...' if summary and len(summary) > 150 else (summary or f"Learn about the {breed['name']}: {breed['temperament']}")
    image_url = breed['image'] if breed['image'].startswith('http') else f"https://yourusername.github.io/dog-breeds/{breed['image']}"
    
    # Replace placeholders in template
    html = template.replace('{{BREED_UUID}}', breed['uuid'])
    html = html.replace('{{BREED_NAME}}', breed['name'])
    html = html.replace('{{BREED_SLUG}}', slug)
    html = html.replace('{{SLUG}}', slug)  # For social sharing
    html = html.replace('{{IMAGE_URL}}', image_url)  # For social sharing
    html = html.replace('{{SUMMARY_PREVIEW}}', summary_preview)  # For social sharing
    html = html.replace('{{GROUP_DISPLAY}}', breed['groupDisplay'])
    html = html.replace('{{TEMPERAMENT_CHIPS}}', temperament_chips)
    html = html.replace('{{SUMMARY_SECTION}}', summary_section)
    html = html.replace('{{SIZE_PHYSICAL_HTML}}', size_physical_html)
    html = html.replace('{{TEMPERAMENT}}', breed['temperament'])
    html = html.replace('{{ENERGY_LEVEL}}', breed['energyLevel'])
    html = html.replace('{{EXERCISE_NEEDS}}', breed.get('exerciseNeeds', 'Moderate exercise'))
    html = html.replace('{{APARTMENT_FRIENDLY}}', apartment_friendly)
    html = html.replace('{{KIDS_FRIENDLY}}', kids_friendly)
    html = html.replace('{{PETS_FRIENDLY}}', pets_friendly)
    html = html.replace('{{STRANGERS}}', strangers)
    html = html.replace('{{ALONE_TIME}}', alone_time)
    html = html.replace('{{FIRST_TIME_OWNER}}', first_time)
    html = html.replace('{{GROOMING}}', grooming_bar)
    html = html.replace('{{SHEDDING}}', breed['shedding'])
    html = html.replace('{{TRAINABILITY}}', trainability_bar)
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
        html_content = f.read()
    
    # Find the preview-section div (this is where breed-specific content starts)
    preview_start = html_content.find('<div class="preview-section" id="preview-section">')
    if preview_start == -1:
        raise ValueError("Could not find preview-section in index.html")
    
    # Header section: everything up to (but not including) the preview-section
    header_section = html_content[:preview_start].rstrip() + '\n        '
    
    # Footer section: find the closing </main> tag and take everything after it
    main_end = html_content.find('</main>', preview_start)
    if main_end == -1:
        raise ValueError("Could not find </main> in index.html")
    
    # Skip past </main> and get everything after
    footer_section = html_content[main_end + len('</main>'):]
    
    # Update breadcrumbs for breed pages
    # Change "All Breeds" to be a link, and add the breed name as current
    breadcrumb_pattern = '''<ul class="breadcrumb" id="breadcrumb">
                <li class="breadcrumb-item">
                    <a href="index.html">Home</a>
                </li>
                <li class="breadcrumb-item">
                    <a href="#" id="breadcrumb-current">All Breeds</a>
                </li>
            </ul>'''
    
    breadcrumb_replacement = '''<ul class="breadcrumb" id="breadcrumb">
                <li class="breadcrumb-item">
                    <a href="../index.html">Home</a>
                </li>
                <li class="breadcrumb-item">
                    <a href="../index.html">All Breeds</a>
                </li>
                <li class="breadcrumb-item">
                    <span id="breadcrumb-current">{{BREED_NAME}}</span>
                </li>
            </ul>'''
    
    if breadcrumb_pattern in header_section:
        header_section = header_section.replace(breadcrumb_pattern, breadcrumb_replacement)
    
    # Build the breed-specific preview-section content
    breed_content = '''<div class="preview-section show" id="preview-section">
            <div class="breed-header">
                <div class="breed-header-content">
                    <h1 class="breed-title">{{BREED_NAME}}</h1>
                    <p class="breed-subtitle">{{GROUP_DISPLAY}}</p>
                    <div class="temperament-chips">
                        {{TEMPERAMENT_CHIPS}}
                    </div>
                </div>
                <a href="http://localhost:5000/breeds/{{BREED_UUID}}/edit" target="_blank" class="btn btn-primary btn-sm edit-breed-btn" title="Edit breed data">
                    <i class="icon icon-edit"></i> Edit
                </a>
            </div>
            
            <div class="breed-content">
                {{SUMMARY_SECTION}}
                
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
                        <h2>Care & Training</h2>
                        <div class="info-grid">
                            <div class="info-item">
                                <div class="info-label">Exercise Needs</div>
                                <div class="info-value">{{EXERCISE_NEEDS}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Grooming Needs</div>
                                <div class="info-value">{{GROOMING}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Shedding</div>
                                <div class="info-value">{{SHEDDING}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Easy to Train</div>
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
            
            <!-- Community Gallery -->
            <div class="community-gallery" id="community-gallery">
                <h2>Meet the {{BREED_NAME}} Community</h2>
                <p class="gallery-subtitle">Real {{BREED_NAME}}s from our community members</p>
                <div id="community-dogs-grid" class="community-dogs-grid">
                    <div class="loading-community">
                        <div class="loading loading-lg"></div>
                        <p>Loading community dogs...</p>
                    </div>
                </div>
                <div class="submit-dog-cta">
                    <p>Have a {{BREED_NAME}}? <a href="../add-dog.html" class="btn btn-primary">Share Your Dog</a></p>
                </div>
            </div>
        </div>
        </main>
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
    header_section = header_section.replace('href="blog.html"', 'href="../blog.html"')
    header_section = header_section.replace('src="images/', 'src="../images/')
    header_section = header_section.replace('href="styles.css"', 'href="../styles.css"')
    
    # Update sidebar links to navigate to browse page with filters
    # Convert data-filter attributes to links that go back to index with hash
    header_section = header_section.replace('id="all-primates-btn"', 'onclick="window.location.href=\'../index.html\'"')
    
    # Add breed-specific CSS before </style>
    breed_css = '''
        .breed-header {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 20px;
        }
        
        .breed-header-content {
            flex: 1;
        }
        
        .edit-breed-btn {
            flex-shrink: 0;
            margin-top: 5px;
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
        
        .temperament-chips {
            margin-top: 1rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .temperament-chips .chip {
            background: #5755d9;
            border: 1px solid #302f79;
            color: #fff;
            font-size: 0.875rem;
            padding: 18px;
            border-radius: 1rem;
            font-weight: 500;
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
    # CSS is now external, no need to inject breed-specific styles
    
    # Add gallery navigation and sidebar navigation script before </body>
    footer_section = footer_section.replace(
        '<script src="dogs.js"></script>',
        '''<script>
        // Image gallery navigation
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
        
        // Sidebar navigation for breed pages
        document.addEventListener('DOMContentLoaded', function() {
            // "View all breeds" button
            const viewAllBtn = document.getElementById('all-primates-btn');
            if (viewAllBtn) {
                viewAllBtn.style.cursor = 'pointer';
            }
            
            // Size filter items - navigate to index with size filter
            document.querySelectorAll('.dog-size-item').forEach(item => {
                item.style.cursor = 'pointer';
                item.addEventListener('click', function() {
                    const size = this.getAttribute('data-value');
                    window.location.href = `../index.html#size-${size}`;
                });
            });
            
            // Group filter items - navigate to index with group filter
            document.querySelectorAll('.subfamily-item[data-filter="group"]').forEach(item => {
                item.style.cursor = 'pointer';
                item.addEventListener('click', function() {
                    const group = this.getAttribute('data-value');
                    window.location.href = `../index.html#group-${group}`;
                });
            });
            
            // Trait checkboxes - navigate to index
            document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    window.location.href = '../index.html';
                });
            });
            
            // Load community dogs for this breed
            loadCommunityDogs();
        });
        
        async function loadCommunityDogs() {
            const breedUuid = '{{BREED_UUID}}';
            const container = document.getElementById('community-dogs-grid');
            
            try {
                const response = await fetch(`http://localhost:5000/api/breeds/${breedUuid}/community-dogs`);
                const data = await response.json();
                
                if (!data.success) {
                    container.innerHTML = '<p style="color: #718096; text-align: center;">Unable to load community dogs</p>';
                    return;
                }
                
                if (data.dogs.length === 0) {
                    container.innerHTML = `
                        <div class="empty-community">
                            <p>Be the first to share your {{BREED_NAME}}!</p>
                            <a href="../add-dog.html" class="btn btn-sm btn-primary">Add Your Dog</a>
                        </div>
                    `;
                    return;
                }
                
                container.innerHTML = data.dogs.map(dog => `
                    <div class="community-dog-card">
                        <img src="${dog.photo_url || 'https://via.placeholder.com/300x250?text=No+Photo'}" 
                             alt="${dog.name}" 
                             class="community-dog-photo">
                        <div class="community-dog-info">
                            <h3 class="community-dog-name">${dog.name}</h3>
                            <p class="community-dog-owner">by ${dog.username}</p>
                            ${dog.public_comment ? `<p class="community-dog-comment">${dog.public_comment}</p>` : ''}
                        </div>
                    </div>
                `).join('');
                
            } catch (error) {
                console.error('Error loading community dogs:', error);
                container.innerHTML = '<p style="color: #e74c3c; text-align: center;">Error loading community dogs</p>';
            }
        }
    </script>'''
    )
    footer_section = footer_section.replace('<script src="app.js"></script>', '')
    footer_section = footer_section.replace('<script src="auth.js"></script>', '<script src="../auth.js"></script>')
    footer_section = footer_section.replace('<script src="dogs.js"></script>', '<script src="../dogs.js"></script>')
    
    # Add community gallery CSS to styles
    breed_specific_css = '''
        .community-gallery {
            margin-top: 60px;
            padding-top: 40px;
            border-top: 2px solid #e2e8f0;
        }
        
        .community-gallery h2 {
            text-align: center;
            color: #2d3748;
            margin-bottom: 8px;
        }
        
        .gallery-subtitle {
            text-align: center;
            color: #718096;
            margin-bottom: 32px;
        }
        
        .community-dogs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }
        
        .loading-community {
            grid-column: 1 / -1;
            text-align: center;
            padding: 40px;
            color: #718096;
        }
        
        .empty-community {
            grid-column: 1 / -1;
            text-align: center;
            padding: 40px;
            color: #718096;
        }
        
        .community-dog-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
            transition: box-shadow 0.2s;
        }
        
        .community-dog-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .community-dog-photo {
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: #f7f8f9;
        }
        
        .community-dog-info {
            padding: 16px;
        }
        
        .community-dog-name {
            font-size: 1.125rem;
            font-weight: 600;
            color: #2d3748;
            margin: 0 0 4px 0;
        }
        
        .community-dog-owner {
            font-size: 0.85rem;
            color: #718096;
            margin: 0 0 8px 0;
        }
        
        .community-dog-comment {
            font-size: 0.9rem;
            color: #4a5568;
            margin: 0;
            line-height: 1.4;
        }
        
        .submit-dog-cta {
            text-align: center;
            padding: 32px;
            background: #f7fafc;
            border-radius: 8px;
        }
        
        .submit-dog-cta p {
            margin: 0;
            color: #4a5568;
            font-size: 1rem;
        }
        
        @media (max-width: 768px) {
            .community-dogs-grid {
                grid-template-columns: 1fr;
            }
        }
    '''
    
    # Insert CSS before closing style tag in header
    header_section = header_section.replace('</style>', breed_specific_css + '\n    </style>')
    
    template = header_section + breed_content + footer_section
    return template

def snake_to_camel(breeds):
    """Convert database snake_case keys to camelCase for template compatibility"""
    converted = []
    for breed in breeds:
        converted_breed = {
            'uuid': breed['uuid'],
            'id': breed.get('legacy_id', breed['uuid']),
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
            'goodWithKids': breed['good_with_kids'],
            'goodWithPets': breed['good_with_pets'],
            'barkingLevel': breed['barking_level'],
            'origin': breed['origin'],
            'summary': breed.get('summary'),
            'image': breed['image_url'],
            'images': breed.get('images', []),
            'wikipediaUrl': breed['wikipedia_url'],
            'apartmentFriendly': breed['apartment_friendly']
        }
        converted.append(converted_breed)
    return converted

def main():
    """Generate all breed pages"""
    # Load breeds from database (has latest data including admin-added images)
    db = breed_db.BreedDB()
    breeds = db.get_all_breeds()
    
    # Add images to each breed
    for breed in breeds:
        images = db.get_breed_images(breed['uuid'])
        # Extract just the URLs from the image objects
        breed['images'] = [img['image_url'] for img in images if not img.get('is_primary')]
    
    # Convert to camelCase for template compatibility
    breeds = snake_to_camel(breeds)
    
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
