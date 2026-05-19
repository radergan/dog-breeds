# API Integration Setup Guide

This guide walks you through setting up Petfinder and Amazon Product Advertising API integrations.

## 🐾 Petfinder API Setup

### 1. Create a Petfinder Account
1. Go to https://www.petfinder.com/user/register/
2. Sign up for a free account
3. Verify your email

### 2. Get API Credentials
1. Visit https://www.petfinder.com/developers/
2. Click "Get an API Key"
3. Fill out the application:
   - **Application Name**: "Dog Breed Finder" (or your site name)
   - **Application URL**: Your site URL (localhost is fine for development)
   - **Description**: "Dog breed database with adoptable dog listings"
4. Accept the terms and submit
5. You'll receive:
   - **API Key** (Client ID)
   - **Secret** (Client Secret)

### 3. Add to .env File
```bash
PETFINDER_API_KEY=your_api_key_here
PETFINDER_API_SECRET=your_secret_here
```

### 4. Test the Integration
```bash
# Test directly
python petfinder_api.py

# Or test via API endpoint
# Start admin panel: python admin.py
# Visit: http://localhost:5000/api/petfinder/test
```

## 🛒 Amazon Product Advertising API Setup

### Important Notes
- You MUST be an approved Amazon Associate (affiliate) first
- Initial approval can take 24-48 hours
- You need at least 3 sales within 180 days to maintain approval

### 1. Join Amazon Associates Program
1. Go to https://affiliate-program.amazon.com/
2. Click "Join Now for Free"
3. Fill out the application:
   - Website URL (your dog breed site)
   - Preferred store ID (your-site-name-20)
   - Website description
   - Topics (select "Pets & Animals")
   - How you drive traffic
4. Submit and wait for approval (usually 1-2 days)

### 2. Get Your Associate Tag
After approval:
1. Log into Amazon Associates Central
2. Your **Associate Tag** (tracking ID) is shown in the top navigation
3. Format: `yoursite-20` (or similar)
4. Save this - you'll need it for affiliate links

### 3. Get API Credentials
1. Go to https://affiliate-program.amazon.com/assoc_credentials/home
2. Look for "Product Advertising API" section
3. Click "Add Credential" or "Manage Credentials"
4. Create new credentials:
   - You'll get an **Access Key**
   - You'll get a **Secret Key** (only shown once - save it!)

⚠️ **IMPORTANT**: Save your Secret Key immediately - you can't retrieve it later!

### 4. Add to .env File
```bash
AMAZON_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
AMAZON_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AMAZON_ASSOCIATE_TAG_US=yoursite-20
```

For other regions (optional):
```bash
AMAZON_ASSOCIATE_TAG_UK=yoursite-21
AMAZON_ASSOCIATE_TAG_CA=yoursite-22
```

### 5. Test the Integration
```bash
# Test directly
python amazon_api.py

# Or test via API endpoint
# Start admin panel: python admin.py
# Visit: http://localhost:5000/api/amazon/test
```

## 📋 Complete .env File Example

```bash
# Petfinder API
PETFINDER_API_KEY=abcdefghijklmnopqrstuvwxyz123456
PETFINDER_API_SECRET=ABCDEFGHIJKLMNOPQRSTUVWXYZ789012

# Amazon Product Advertising API
AMAZON_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
AMAZON_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AMAZON_ASSOCIATE_TAG_US=dogbreeds-20

# (Optional) Other regions
AMAZON_ASSOCIATE_TAG_UK=dogbreeds-21
AMAZON_ASSOCIATE_TAG_CA=dogbreeds-22
```

## 🚀 Using the APIs

### Petfinder API Usage

**Get adoptable dogs for a breed:**
```bash
GET http://localhost:5000/api/adoptable-dogs?breed=Labrador%20Retriever&location=60601&distance=50
```

**Response:**
```json
{
  "success": true,
  "count": 20,
  "total": 156,
  "dogs": [
    {
      "id": 12345678,
      "name": "Max",
      "age": "Adult",
      "gender": "Male",
      "size": "Large",
      "photo": "https://...",
      "url": "https://www.petfinder.com/...",
      "location": {
        "city": "Chicago",
        "state": "IL"
      }
    }
  ]
}
```

### Amazon Product API Usage

**Get product recommendations for a breed:**
```bash
GET http://localhost:5000/api/products/golden-retriever
```

**Response:**
```json
{
  "success": true,
  "breed": "Golden Retriever",
  "size": "Large",
  "products": {
    "food": [...],
    "toys": [...],
    "grooming": [...],
    "collars": [...],
    "beds": [...],
    "crates": [...]
  }
}
```

**Get specific product categories only:**
```bash
GET http://localhost:5000/api/products/golden-retriever?categories=toys,food
```

## 🔧 Frontend Integration

Add to breed page HTML to display adoptable dogs:

```html
<div id="adoptable-dogs">
  <h2>Adoptable [Breed Name]s Near You</h2>
  <div class="location-input">
    <input type="text" id="location" placeholder="Enter ZIP code">
    <button onclick="loadAdoptableDogs()">Search</button>
  </div>
  <div id="dogs-list"></div>
</div>

<script>
async function loadAdoptableDogs() {
  const breed = 'Labrador Retriever'; // From page data
  const location = document.getElementById('location').value;
  
  const response = await fetch(
    `http://localhost:5000/api/adoptable-dogs?breed=${breed}&location=${location}`
  );
  const data = await response.json();
  
  // Render dogs...
}
</script>
```

Add to breed page to display products:

```html
<div id="product-recommendations">
  <h2>Recommended Products for [Breed Name]</h2>
  <div id="products-list"></div>
</div>

<script>
async function loadProducts() {
  const breedSlug = 'labrador-retriever'; // From page data
  
  const response = await fetch(
    `http://localhost:5000/api/products/${breedSlug}?categories=toys,food,grooming`
  );
  const data = await response.json();
  
  // Render products with affiliate links...
}
</script>
```

## 🔒 Rate Limits

### Petfinder
- **1,000 requests per day** (free tier)
- Token expires after 1 hour (auto-refreshed by our client)
- Use caching to reduce API calls

### Amazon
- **1 request per second** (default)
- **8,640 requests per day**
- Exceeded limits result in throttling
- Cache product data for 24 hours minimum

## 💰 Making Money with Amazon

### Commission Rates (as of 2024)
- Pet Products: **4.5%**
- Kitchen Items: **3%**
- Home Products: **3%**
- Electronics: **1%**

### Example Earnings
If someone clicks your affiliate link and buys:
- $50 dog bed = $2.25 commission
- $30 grooming kit = $1.35 commission
- $80 crate = $3.60 commission

**Important**: Amazon gives you commission on the entire shopping cart, not just the item you linked to!

### Best Practices
1. Link to products you actually recommend
2. Don't hide that you're using affiliate links (add disclosure)
3. Update product links regularly (products go out of stock)
4. Focus on categories with higher commission rates
5. Create "starter kits" with multiple products

## 📝 Disclosure Requirements

You MUST disclose affiliate relationships. Add to your pages:

```html
<p class="affiliate-disclosure">
  <small>
    We are a participant in the Amazon Services LLC Associates Program, 
    an affiliate advertising program designed to provide a means for us 
    to earn fees by linking to Amazon.com and affiliated sites.
  </small>
</p>
```

## ❓ Troubleshooting

### Petfinder API Issues

**"API key not found"**
- Check that PETFINDER_API_KEY is set in .env
- Make sure you're loading the .env file (`python-dotenv`)

**"Invalid breed name"**
- Breed names must match exactly (case-sensitive)
- Use `/api/petfinder/test` to see valid breed names

### Amazon API Issues

**"Invalid signature"**
- Check that your secret key is correct
- Make sure there are no extra spaces in .env
- Secret key is case-sensitive

**"Invalid AssociateTag"**
- Your Associate Tag must be active and approved
- Format must be exactly as shown in Associates Central
- Usually ends in `-20` or similar

**"You are not authorized to use this API"**
- You need to be approved as an Amazon Associate first
- Wait 24-48 hours after approval before using PA-API

## 🎯 Next Steps

1. ✅ Get API credentials for both services
2. ✅ Add credentials to `.env` file
3. ✅ Test both integrations using test endpoints
4. ⬜ Update breed page template to show adoptable dogs
5. ⬜ Update breed page template to show product recommendations
6. ⬜ Add location detection for better Petfinder results
7. ⬜ Implement caching to reduce API calls
8. ⬜ Add Amazon disclosure statement to pages
9. ⬜ Track affiliate clicks and conversions

## 📚 Additional Resources

- [Petfinder API Documentation](https://www.petfinder.com/developers/v2/docs/)
- [Amazon PA-API Documentation](https://webservices.amazon.com/paapi5/documentation/)
- [Amazon Associates Help](https://affiliate-program.amazon.com/help)
- [FTC Affiliate Disclosure Guidelines](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers)
