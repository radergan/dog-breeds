// Main application logic

let currentDogs = [...dogs];
let currentFilter = '';
let currentFilterValue = '';
let currentFilterDogs = [];

// Helper function to create URL-friendly slugs
function createSlug(name) {
    return name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
}

// DOM Elements
const searchInput = document.getElementById('search-input');
const speciesCount = document.getElementById('species-count');
const previewSection = document.getElementById('preview-section');
const previewGrid = document.getElementById('preview-grid');
const previewList = document.getElementById('preview-list');
const previewTitle = document.getElementById('preview-title');
const breadcrumb = document.getElementById('breadcrumb');
const breadcrumbCurrent = document.getElementById('breadcrumb-current');

// View toggle functionality for breeds
const breedListViewBtn = document.getElementById('breed-list-view-btn');
const breedGalleryViewBtn = document.getElementById('breed-gallery-view-btn');

// Load saved view preference (default: gallery for breeds)
let currentBreedView = localStorage.getItem('breedView') || 'gallery';

function setBreedView(view) {
    currentBreedView = view;
    localStorage.setItem('breedView', view);
    
    if (view === 'list') {
        if (previewGrid) previewGrid.style.display = 'none';
        if (previewList) previewList.style.display = 'block';
        if (breedListViewBtn) breedListViewBtn.classList.add('active');
        if (breedGalleryViewBtn) breedGalleryViewBtn.classList.remove('active');
    } else {
        if (previewGrid) previewGrid.style.display = 'grid';
        if (previewList) previewList.style.display = 'none';
        if (breedListViewBtn) breedListViewBtn.classList.remove('active');
        if (breedGalleryViewBtn) breedGalleryViewBtn.classList.add('active');
    }
    
    // Re-render to update the view
    renderPage();
}

if (breedListViewBtn) {
    breedListViewBtn.addEventListener('click', () => setBreedView('list'));
}
if (breedGalleryViewBtn) {
    breedGalleryViewBtn.addEventListener('click', () => setBreedView('gallery'));
}

// Set initial view
setBreedView(currentBreedView);

// Update stats (if element exists)
if (speciesCount) {
    speciesCount.textContent = dogs.length;
}

// Update breed count badge in sidebar
const breedCountBadge = document.getElementById('breed-count-badge');
if (breedCountBadge) {
    breedCountBadge.textContent = dogs.length;
}

// Update breadcrumbs
function updateBreadcrumbs(filterType, filterName) {
    if (!filterType && !filterName) {
        // Show "Home > All Breeds"
        breadcrumb.innerHTML = `
            <li class="breadcrumb-item">
                <a href="index.html">Home</a>
            </li>
            <li class="breadcrumb-item">
                <a href="#">All Breeds</a>
            </li>
        `;
    } else {
        // Show "Home > Filter Type > Filter Name"
        breadcrumb.innerHTML = `
            <li class="breadcrumb-item">
                <a href="index.html">Home</a>
            </li>
            <li class="breadcrumb-item">
                <a href="#">${filterType}</a>
            </li>
            <li class="breadcrumb-item">
                <a href="#">${filterName}</a>
            </li>
        `;
    }
}

// All Breeds button
const allPrimatesBtn = document.getElementById('all-primates-btn');
if (allPrimatesBtn) {
    allPrimatesBtn.addEventListener('click', () => {
        // Remove active from all filter items
        document.querySelectorAll('.subfamily-item, .dog-size-item').forEach(i => i.classList.remove('active'));
        
        // Add active to all breeds button
        allPrimatesBtn.classList.add('active');
        
        // Clear current filter
        currentFilter = '';
        currentFilterValue = '';
        
        // Update breadcrumbs
        updateBreadcrumbs();
        
        // Show all breeds sorted A-Z
        showAllDogs();
    });
}

// Show all dog breeds sorted alphabetically
function showAllDogs() {
    // Sort dogs alphabetically by name
    const sortedDogs = [...dogs].sort((a, b) => 
        a.name.toLowerCase().localeCompare(b.name.toLowerCase())
    );
    
    // Store current dogs
    currentFilterDogs = sortedDogs;
    
    // Update preview title
    previewTitle.textContent = `All Dog Breeds`;
    
    // Update breadcrumbs
    updateBreadcrumbs();
    
    // Render current page
    renderPage();
    
    // Show the preview section
    previewSection.classList.add('show');
}

// Load all dogs on page load
showAllDogs();

// Check for hash in URL and open corresponding dog breed
if (window.location.hash) {
    const hash = window.location.hash.substring(1); // Remove #
    // Find dog by slug (e.g., #golden-retriever)
    const dog = dogs.find(d => createSlug(d.name) === hash);
    if (dog) {
        showDogModal(dog);
    }
}

// Filter selection (handles both subfamily-item and dog-size-item)
document.querySelectorAll('.subfamily-item, .dog-size-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.stopPropagation();
        const filter = item.dataset.filter;
        const value = item.dataset.value;
        
        // Skip if this is the "View all" button (it has its own handler)
        if (!filter || !value) return;
        
        // Remove active from all filter items and all breeds button
        document.querySelectorAll('.subfamily-item, .dog-size-item').forEach(i => i.classList.remove('active'));
        if (allPrimatesBtn) allPrimatesBtn.classList.remove('active');
        
        // Add active to clicked item
        item.classList.add('active');
        
        // Set current filter
        currentFilter = filter;
        currentFilterValue = value;
        
        // Show preview section with filtered breeds
        showFiltered(filter, value);
    });
});

// Show preview cards for a filter
function showFiltered(filter, value) {
    // Get dogs for this filter
    let filteredDogs = [];
    if (filter === 'size') {
        filteredDogs = dogs.filter(d => d.size === value);
    } else if (filter === 'shedding') {
        filteredDogs = dogs.filter(d => d.shedding === value);
    } else if (filter === 'group') {
        filteredDogs = dogs.filter(d => d.group === value);
    } else if (filter === 'apartmentFriendly') {
        filteredDogs = dogs.filter(d => d.apartmentFriendly === value);
    } else if (filter === 'firstTimeOwner') {
        filteredDogs = dogs.filter(d => d.firstTimeOwner === value);
    } else if (filter === 'toleratesBeingAlone') {
        filteredDogs = dogs.filter(d => d.toleratesBeingAlone === value);
    } else if (filter === 'goodWithStrangers') {
        filteredDogs = dogs.filter(d => d.goodWithStrangers === value);
    }
    
    if (filteredDogs.length === 0) {
        previewSection.classList.remove('show');
        return;
    }
    
    // Store current filtered dogs
    currentFilterDogs = filteredDogs;
    
    // Update preview title
    const filterElement = document.querySelector(`[data-filter="${filter}"][data-value="${value}"]`);
    const filterName = (filterElement.querySelector('.subfamily-name') || filterElement.querySelector('.dog-size-name')).textContent;
    const filterType = filter.charAt(0).toUpperCase() + filter.slice(1);
    previewTitle.textContent = `${filterName}`;
    
    // Update breadcrumbs
    updateBreadcrumbs(filterType, filterName);
    
    // Render current page
    renderPage();
    
    // Show the preview section
    previewSection.classList.add('show');
}

// Render preview cards
function renderPage() {
    // Render gallery view
    if (previewGrid) {
        previewGrid.innerHTML = currentFilterDogs.map(dog => {
            const slug = createSlug(dog.name);
            return `
            <a href="breeds/${slug}.html" class="preview-card">
                <img src="${dog.image}" alt="${dog.name}" class="preview-image">
                <div class="preview-name">${dog.name}</div>
            </a>`;
        }).join('');
    }
    
    // Render list view
    if (previewList) {
        previewList.innerHTML = currentFilterDogs.map(dog => {
            const slug = createSlug(dog.name);
            const temperamentChips = dog.temperament 
                ? dog.temperament.split(',').map(trait => `<span class="chip">${trait.trim()}</span>`).join('')
                : '';
            return `
            <a href="breeds/${slug}.html" class="breed-list-item">
                <img src="${dog.image}" alt="${dog.name}" class="breed-list-image">
                <div class="breed-list-content">
                    <span class="breed-list-group">${dog.groupDisplay}</span>
                    <div class="breed-list-name">${dog.name}</div>
                    <div class="breed-list-temperament">${temperamentChips}</div>
                    <div class="breed-list-meta">
                        <span>Size: ${dog.size}</span>
                        <span>Weight: ${dog.weight}</span>
                        <span>Shedding: ${dog.shedding}</span>
                    </div>
                </div>
                <div class="breed-list-actions">
                    <span class="breed-list-link">View Details</span>
                </div>
            </a>`;
        }).join('');
    }
}



// Search functionality
searchInput.addEventListener('input', (e) => {
    filterDogs();
});

// Search button click
const searchBtn = document.getElementById('search-btn');
if (searchBtn) {
    searchBtn.addEventListener('click', (e) => {
        filterDogs();
    });
}

// Filter dogs based on search and current filter
function filterDogs() {
    const searchTerm = searchInput.value.toLowerCase();
    
    // If search is empty and no filter/all breeds active, do nothing
    if (!searchTerm && !currentFilter && !allPrimatesBtn.classList.contains('active')) return;
    
    // If search has content but nothing is active, activate all breeds view first
    if (searchTerm && !currentFilter && !allPrimatesBtn.classList.contains('active')) {
        showAllDogs();
        return;
    }
    
    const filtered = dogs.filter(dog => {
        const matchesSearch = 
            dog.name.toLowerCase().includes(searchTerm) ||
            dog.groupDisplay.toLowerCase().includes(searchTerm) ||
            dog.temperament.toLowerCase().includes(searchTerm) ||
            dog.size.toLowerCase().includes(searchTerm) ||
            dog.shedding.toLowerCase().includes(searchTerm);
        
        let matchesFilter = true;
        if (currentFilter && currentFilterValue) {
            if (currentFilter === 'size') {
                matchesFilter = dog.size === currentFilterValue;
            } else if (currentFilter === 'shedding') {
                matchesFilter = dog.shedding === currentFilterValue;
            } else if (currentFilter === 'group') {
                matchesFilter = dog.group === currentFilterValue;
            }
        }
        
        return matchesSearch && matchesFilter;
    }).sort((a, b) => 
        a.name.toLowerCase().localeCompare(b.name.toLowerCase())
    );
    
    // Store filtered results
    currentFilterDogs = filtered;
    
    // Update the preview section title
    let titleText;
    if (currentFilter && currentFilterValue) {
        const filterElement = document.querySelector(`[data-filter="${currentFilter}"][data-value="${currentFilterValue}"]`);
        const filterNameElement = filterElement.querySelector('.subfamily-name') || filterElement.querySelector('.dog-size-name');
        titleText = filterNameElement ? filterNameElement.textContent : currentFilterValue;
    } else {
        titleText = `All Dog Breeds`;
    }
    previewTitle.textContent = titleText;
    
    // Render current page
    renderPage();
}

// Add keyboard shortcut for search
document.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement !== searchInput) {
        e.preventDefault();
        searchInput.focus();
    }
});

// Checkbox filtering for traits
const activeCheckboxFilters = new Set();

document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', (e) => {
        const filter = checkbox.dataset.filter;
        const value = checkbox.dataset.value;
        const filterKey = `${filter}:${value}`;
        
        if (checkbox.checked) {
            activeCheckboxFilters.add(filterKey);
        } else {
            activeCheckboxFilters.delete(filterKey);
        }
        
        // Apply checkbox filters
        applyCheckboxFilters();
    });
});

function applyCheckboxFilters() {
    if (activeCheckboxFilters.size === 0) {
        // No checkbox filters active, show current view or all dogs
        if (currentFilter && currentFilterValue) {
            showFiltered(currentFilter, currentFilterValue);
        } else if (allPrimatesBtn && allPrimatesBtn.classList.contains('active')) {
            showAllDogs();
        }
        return;
    }
    
    // If nothing is active yet, activate all breeds view first
    if (!currentFilter && !currentFilterValue && (!allPrimatesBtn || !allPrimatesBtn.classList.contains('active'))) {
        if (allPrimatesBtn) {
            allPrimatesBtn.classList.add('active');
        }
    }
    
    // Start with current filtered dogs or all dogs
    let baselineDogs = currentFilter && currentFilterValue 
        ? dogs.filter(dog => {
            if (currentFilter === 'size') return dog.size === currentFilterValue;
            if (currentFilter === 'group') return dog.group === currentFilterValue;
            return true;
        })
        : [...dogs];
    
    // Apply each checkbox filter
    const filteredDogs = baselineDogs.filter(dog => {
        for (let filterKey of activeCheckboxFilters) {
            const [filter, value] = filterKey.split(':');
            
            if (filter === 'shedding' && dog.shedding !== value) {
                return false;
            }
            if (filter === 'goodWithKids' && dog.goodWithKids !== true) {
                return false;
            }
            if (filter === 'goodWithPets' && dog.goodWithPets !== true) {
                return false;
            }
        }
        return true;
    });
    
    // Sort alphabetically
    filteredDogs.sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));
    
    // Store and render
    currentFilterDogs = filteredDogs;
    
    // Update title
    const filterCount = activeCheckboxFilters.size;
    const baseTitle = currentFilter && currentFilterValue 
        ? document.querySelector(`[data-filter="${currentFilter}"][data-value="${currentFilterValue}"]`)?.textContent?.trim() || 'Filtered'
        : 'All Dog Breeds';
    previewTitle.textContent = `${baseTitle} (${filterCount} filter${filterCount > 1 ? 's' : ''} applied)`;
    
    // Render
    renderPage();
    
    // Show preview section
    previewSection.classList.add('show');
}

// Gallery state
let currentGalleryIndex = 0;
let currentGalleryImages = [];

// Show dog detail modal
function showDogModal(dog) {
    const modal = document.getElementById('primate-modal');
    const video = document.getElementById('modal-video');
    const image = document.getElementById('modal-avatar');
    const prevBtn = document.getElementById('gallery-prev');
    const nextBtn = document.getElementById('gallery-next');
    const indicator = document.getElementById('gallery-indicator');
    
    // Reset gallery state
    currentGalleryIndex = 0;
    currentGalleryImages = dog.images || [dog.image];
    
    // No video for dogs, show gallery immediately
    video.classList.remove('active');
    video.src = '';
    image.style.display = 'block';
    updateGallery();
    
    // Populate modal content
    document.getElementById('modal-avatar').alt = dog.name;
    document.getElementById('modal-header-title').textContent = dog.name;
    document.getElementById('modal-title').textContent = dog.name;
    document.getElementById('modal-scientific').textContent = `${dog.groupDisplay}`;
    
    // Dog-specific fields
    document.getElementById('modal-family').textContent = dog.groupDisplay;
    
    // Size & Weight
    document.getElementById('modal-size').textContent = `${dog.size} - ${dog.weight || 'Weight varies'} - ${dog.height || 'Height varies'}`;
    
    // Temperament
    document.getElementById('modal-temperament').textContent = dog.temperament;
    
    // Energy Level & Exercise
    const exerciseText = dog.exerciseNeeds ? `${dog.energyLevel} - ${dog.exerciseNeeds}` : dog.energyLevel;
    document.getElementById('modal-energy').textContent = exerciseText;
    
    // Living Situation (Apartment-Friendly)
    document.getElementById('modal-apartment').textContent = dog.apartmentFriendly || 'Unknown';
    
    // Family Friendly
    const kidsText = dog.goodWithKids === true ? 'Yes' : dog.goodWithKids === false ? 'No' : dog.goodWithKids;
    const petsText = typeof dog.goodWithPets === 'boolean' ? (dog.goodWithPets ? 'Yes' : 'No') : dog.goodWithPets;
    document.getElementById('modal-family-friendly').textContent = `Kids: ${kidsText} | Pets: ${petsText}`;
    
    // With Strangers
    document.getElementById('modal-strangers').textContent = dog.goodWithStrangers || 'Unknown';
    
    // Can Be Left Alone
    document.getElementById('modal-alone').textContent = dog.toleratesBeingAlone || 'Unknown';
    
    // First-Time Owner
    document.getElementById('modal-first-time').textContent = dog.firstTimeOwner || 'Unknown';
    
    // Grooming & Shedding
    document.getElementById('modal-grooming').textContent = `${dog.groomingNeeds} | ${dog.shedding}`;
    
    // Trainability
    const barkingText = dog.barkingLevel ? ` | Barking: ${dog.barkingLevel}` : '';
    document.getElementById('modal-trainability').textContent = `${dog.trainability}${barkingText}`;
    
    // Lifespan & Origin
    const originText = dog.origin ? ` | Origin: ${dog.origin}` : '';
    document.getElementById('modal-lifespan').textContent = `${dog.lifespan}${originText}`;
    
    // Wikipedia link
    const linksSection = document.getElementById('modal-links-section');
    const linksValue = document.getElementById('modal-links');
    if (dog.wikipediaUrl) {
        linksValue.innerHTML = `<a href="${dog.wikipediaUrl}" target="_blank" style="color: #5755d9;">Wikipedia Article →</a>`;
        linksSection.style.display = 'block';
    } else {
        linksSection.style.display = 'none';
    }
    
    // Set direct link
    const directLinkInput = document.getElementById('modal-direct-link');
    const slug = createSlug(dog.name);
    const directLink = `${window.location.origin}${window.location.pathname}#${slug}`;
    directLinkInput.value = directLink;
    
    // Update URL hash
    window.history.pushState(null, '', `#${slug}`);
    
    // Show modal
    modal.classList.add('active');
}

// Update gallery display
function updateGallery() {
    const image = document.getElementById('modal-avatar');
    const prevBtn = document.getElementById('gallery-prev');
    const nextBtn = document.getElementById('gallery-next');
    const indicator = document.getElementById('gallery-indicator');
    
    // Update image
    image.src = currentGalleryImages[currentGalleryIndex];
    
    // Show/hide navigation if multiple images
    if (currentGalleryImages.length > 1) {
        prevBtn.classList.add('active');
        nextBtn.classList.add('active');
        indicator.classList.add('active');
        indicator.textContent = `Image ${currentGalleryIndex + 1} of ${currentGalleryImages.length}`;
    } else {
        prevBtn.classList.remove('active');
        nextBtn.classList.remove('active');
        indicator.classList.remove('active');
    }
}

// Gallery navigation
document.getElementById('gallery-prev').addEventListener('click', (e) => {
    e.stopPropagation();
    currentGalleryIndex = (currentGalleryIndex - 1 + currentGalleryImages.length) % currentGalleryImages.length;
    updateGallery();
});

document.getElementById('gallery-next').addEventListener('click', (e) => {
    e.stopPropagation();
    currentGalleryIndex = (currentGalleryIndex + 1) % currentGalleryImages.length;
    updateGallery();
});

// Close modal when clicking overlay or close button
document.querySelectorAll('#primate-modal .modal-overlay, #primate-modal .btn-clear').forEach(el => {
    el.addEventListener('click', (e) => {
        e.preventDefault();
        const modal = document.getElementById('primate-modal');
        const video = document.getElementById('modal-video');
        
        // Stop video and reset
        video.pause();
        video.src = '';
        video.classList.remove('active');
        
        // Clear hash from URL
        window.history.pushState(null, '', window.location.pathname);
        
        modal.classList.remove('active');
    });
});

// Close modal with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modal = document.getElementById('primate-modal');
        const video = document.getElementById('modal-video');
        
        // Stop video and reset
        video.pause();
        video.src = '';
        video.classList.remove('active');
        
        // Clear hash from URL
        window.history.pushState(null, '', window.location.pathname);
        
        // Clear hash from URL
        window.history.pushState(null, '', window.location.pathname);
        
        modal.classList.remove('active');
    }
});
