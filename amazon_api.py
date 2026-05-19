"""
Amazon Product Advertising API (PA-API) Integration
https://webservices.amazon.com/paapi5/documentation/
"""
import os
import hmac
import hashlib
import base64
from datetime import datetime
from urllib.parse import quote, urlencode
import requests
from typing import List, Dict, Optional

class AmazonProductAPI:
    """Client for Amazon Product Advertising API 5.0"""
    
    # PA-API endpoints by region
    ENDPOINTS = {
        'us': 'webservices.amazon.com',
        'uk': 'webservices.amazon.co.uk',
        'ca': 'webservices.amazon.ca',
    }
    
    # Associate tags (your affiliate IDs)
    ASSOCIATE_TAGS = {
        'us': os.environ.get('AMAZON_ASSOCIATE_TAG_US', ''),
        'uk': os.environ.get('AMAZON_ASSOCIATE_TAG_UK', ''),
        'ca': os.environ.get('AMAZON_ASSOCIATE_TAG_CA', ''),
    }
    
    def __init__(self, access_key: str, secret_key: str, region: str = 'us'):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.endpoint = self.ENDPOINTS[region]
        self.associate_tag = self.ASSOCIATE_TAGS[region]
        
        if not self.associate_tag:
            raise ValueError(f"AMAZON_ASSOCIATE_TAG_{region.upper()} not set in environment")
    
    def _sign_request(self, method: str, uri: str, query_string: str, payload: str, timestamp: str) -> str:
        """Create AWS Signature Version 4"""
        
        # Task 1: Create canonical request
        canonical_headers = f"host:{self.endpoint}\nx-amz-date:{timestamp}\n"
        signed_headers = "host;x-amz-date"
        
        payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        
        canonical_request = f"{method}\n{uri}\n{query_string}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        
        # Task 2: Create string to sign
        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{timestamp[:8]}/us-east-1/ProductAdvertisingAPI/aws4_request"
        canonical_request_hash = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        
        string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{canonical_request_hash}"
        
        # Task 3: Calculate signature
        def sign(key, msg):
            return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
        
        k_date = sign(('AWS4' + self.secret_key).encode('utf-8'), timestamp[:8])
        k_region = sign(k_date, 'us-east-1')
        k_service = sign(k_region, 'ProductAdvertisingAPI')
        k_signing = sign(k_service, 'aws4_request')
        
        signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # Task 4: Add signature to request
        authorization = f"{algorithm} Credential={self.access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        
        return authorization
    
    def _make_request(self, operation: str, payload: dict) -> dict:
        """Make signed request to Amazon PA-API"""
        
        # Add required fields
        payload['PartnerTag'] = self.associate_tag
        payload['PartnerType'] = 'Associates'
        
        # Prepare request
        uri = '/paapi5/searchitems'
        method = 'POST'
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        
        import json
        body = json.dumps(payload)
        
        # Sign request
        authorization = self._sign_request(method, uri, '', body, timestamp)
        
        # Make request
        url = f"https://{self.endpoint}{uri}"
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Amz-Date': timestamp,
            'Authorization': authorization,
            'X-Amz-Target': f'com.amazon.paapi5.v1.ProductAdvertisingAPIv1.{operation}',
            'Content-Encoding': 'amz-1.0'
        }
        
        response = requests.post(url, data=body, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def search_products(self, keywords: str, 
                       category: str = None,
                       min_price: int = None,
                       max_price: int = None,
                       item_count: int = 10) -> List[Dict]:
        """
        Search for products on Amazon
        
        Args:
            keywords: Search keywords (e.g., "large dog harness")
            category: Category to search in (e.g., "PetSupplies")
            min_price: Minimum price in cents (e.g., 1000 = $10.00)
            max_price: Maximum price in cents
            item_count: Number of results (max 10)
        
        Returns:
            List of product dicts with title, price, image, url, etc.
        """
        
        payload = {
            'Keywords': keywords,
            'Resources': [
                'Images.Primary.Large',
                'ItemInfo.Title',
                'ItemInfo.Features',
                'Offers.Listings.Price',
                'Offers.Listings.Availability.Message'
            ],
            'ItemCount': min(item_count, 10),
            'Marketplace': f'www.amazon.{self.region}'
        }
        
        if category:
            payload['SearchIndex'] = category
        
        if min_price:
            payload['MinPrice'] = min_price
        
        if max_price:
            payload['MaxPrice'] = max_price
        
        try:
            result = self._make_request('SearchItems', payload)
            return self._parse_search_results(result)
        except Exception as e:
            print(f"Amazon API error: {e}")
            return []
    
    def _parse_search_results(self, response: dict) -> List[Dict]:
        """Parse API response into simplified product list"""
        products = []
        
        if 'SearchResult' not in response or 'Items' not in response['SearchResult']:
            return products
        
        for item in response['SearchResult']['Items']:
            product = {
                'asin': item['ASIN'],
                'title': item.get('ItemInfo', {}).get('Title', {}).get('DisplayValue', ''),
                'url': item.get('DetailPageURL', ''),
                'image': None,
                'price': None,
                'currency': 'USD',
                'availability': None,
                'features': []
            }
            
            # Extract image
            if 'Images' in item and 'Primary' in item['Images']:
                product['image'] = item['Images']['Primary']['Large']['URL']
            
            # Extract price
            if 'Offers' in item and 'Listings' in item['Offers']:
                listing = item['Offers']['Listings'][0]
                if 'Price' in listing:
                    product['price'] = listing['Price'].get('Amount')
                    product['currency'] = listing['Price'].get('Currency', 'USD')
                if 'Availability' in listing:
                    product['availability'] = listing['Availability'].get('Message')
            
            # Extract features
            if 'ItemInfo' in item and 'Features' in item['ItemInfo']:
                features = item['ItemInfo']['Features'].get('DisplayValues', [])
                product['features'] = features[:5]  # Limit to 5 features
            
            products.append(product)
        
        return products


def get_breed_specific_products(breed_name: str, breed_size: str, 
                                coat_type: str = None) -> Dict[str, List[Dict]]:
    """
    Get product recommendations for a specific dog breed
    
    Args:
        breed_name: Full breed name (e.g., "Golden Retriever")
        breed_size: "Small", "Medium", or "Large"
        coat_type: Optional coat type for grooming products
    
    Returns:
        Dict with categories (food, toys, grooming, etc.) and product lists
    """
    
    try:
        api = AmazonProductAPI(
            os.environ.get('AMAZON_ACCESS_KEY'),
            os.environ.get('AMAZON_SECRET_KEY')
        )
    except Exception as e:
        print(f"Error initializing Amazon API: {e}")
        return {}
    
    products = {}
    
    # Size-based product searches
    size_map = {
        'Small': 'small',
        'Medium': 'medium',
        'Large': 'large'
    }
    size_keyword = size_map.get(breed_size, 'medium')
    
    # Category 1: Food & Treats
    products['food'] = api.search_products(
        f"{size_keyword} breed dog food",
        category='PetSupplies',
        item_count=5
    )
    
    # Category 2: Collars & Leashes
    products['collars'] = api.search_products(
        f"{size_keyword} dog collar leash",
        category='PetSupplies',
        item_count=5
    )
    
    # Category 3: Toys
    products['toys'] = api.search_products(
        f"{size_keyword} dog toys durable",
        category='PetSupplies',
        item_count=5
    )
    
    # Category 4: Beds
    products['beds'] = api.search_products(
        f"{size_keyword} dog bed",
        category='PetSupplies',
        item_count=5
    )
    
    # Category 5: Grooming (coat-specific if provided)
    if coat_type:
        grooming_query = f"dog brush {coat_type} coat"
    else:
        grooming_query = f"{size_keyword} dog grooming"
    
    products['grooming'] = api.search_products(
        grooming_query,
        category='PetSupplies',
        item_count=5
    )
    
    # Category 6: Crates & Carriers
    products['crates'] = api.search_products(
        f"{size_keyword} dog crate",
        category='PetSupplies',
        item_count=5
    )
    
    return products


if __name__ == "__main__":
    # Test the API
    try:
        print("Testing Amazon Product API...")
        
        api = AmazonProductAPI(
            os.environ.get('AMAZON_ACCESS_KEY'),
            os.environ.get('AMAZON_SECRET_KEY')
        )
        
        results = api.search_products("large dog harness", category='PetSupplies', item_count=5)
        
        print(f"\nFound {len(results)} products:\n")
        for product in results:
            print(f"- {product['title']}")
            print(f"  Price: ${product['price']} {product['currency']}" if product['price'] else "  Price: N/A")
            print(f"  URL: {product['url']}\n")
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nTo test, add to .env file:")
        print("AMAZON_ACCESS_KEY=your_access_key")
        print("AMAZON_SECRET_KEY=your_secret_key")
        print("AMAZON_ASSOCIATE_TAG_US=your_affiliate_tag")
