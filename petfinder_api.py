"""
Petfinder API Integration
https://www.petfinder.com/developers/v2/docs/
"""
import requests
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class PetfinderAPI:
    """Client for Petfinder API v2"""
    
    BASE_URL = "https://api.petfinder.com/v2"
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = None
        self.token_expires_at = None
    
    def _get_access_token(self):
        """Get OAuth2 access token"""
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token
        
        # Request new token
        url = f"{self.BASE_URL}/oauth2/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.api_secret
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        # Token expires in 3600 seconds, refresh 5 min early
        self.token_expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'] - 300)
        
        return self.access_token
    
    def _make_request(self, endpoint: str, params: dict = None):
        """Make authenticated request to Petfinder API"""
        token = self._get_access_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def search_dogs(self, breed: str = None, location: str = None, 
                    distance: int = 50, limit: int = 20, page: int = 1,
                    sort: str = 'distance') -> Dict:
        """
        Search for adoptable dogs
        
        Args:
            breed: Breed name (e.g., "Labrador Retriever")
            location: ZIP code or "city, state" (e.g., "90210" or "Chicago, IL")
            distance: Distance in miles (default 50)
            limit: Results per page (max 100, default 20)
            page: Page number (default 1)
            sort: Sort order ('recent', 'distance', '-recent', '-distance')
        
        Returns:
            Dict with 'animals' list and 'pagination' info
        """
        params = {
            'type': 'dog',
            'limit': limit,
            'page': page,
            'sort': sort
        }
        
        if breed:
            params['breed'] = breed
        
        if location:
            params['location'] = location
            params['distance'] = distance
        
        return self._make_request('/animals', params)
    
    def get_animal(self, animal_id: int) -> Dict:
        """Get details for a specific animal"""
        return self._make_request(f'/animals/{animal_id}')
    
    def get_breeds(self) -> List[str]:
        """Get list of all dog breeds in Petfinder"""
        data = self._make_request('/types/dog/breeds')
        return [breed['name'] for breed in data['breeds']]
    
    def search_organizations(self, location: str = None, 
                           distance: int = 50, 
                           limit: int = 20) -> Dict:
        """Search for animal shelters/rescues"""
        params = {
            'limit': limit
        }
        
        if location:
            params['location'] = location
            params['distance'] = distance
        
        return self._make_request('/organizations', params)


def get_petfinder_client():
    """Factory function to create Petfinder client from environment variables"""
    api_key = os.environ.get('PETFINDER_API_KEY')
    api_secret = os.environ.get('PETFINDER_API_SECRET')
    
    if not api_key or not api_secret:
        raise ValueError("PETFINDER_API_KEY and PETFINDER_API_SECRET must be set in environment")
    
    return PetfinderAPI(api_key, api_secret)


if __name__ == "__main__":
    # Test the API
    try:
        client = get_petfinder_client()
        
        # Test search
        print("Testing Petfinder API...")
        results = client.search_dogs(breed="Labrador Retriever", location="60601", limit=5)
        
        print(f"\nFound {results['pagination']['total_count']} Labrador Retrievers")
        print(f"Showing {len(results['animals'])} results:\n")
        
        for animal in results['animals']:
            print(f"- {animal['name']}: {animal['age']}, {animal['gender']}")
            print(f"  Location: {animal['contact']['address']['city']}, {animal['contact']['address']['state']}")
            print(f"  URL: {animal['url']}\n")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("\nTo test, add to .env file:")
        print("PETFINDER_API_KEY=your_key_here")
        print("PETFINDER_API_SECRET=your_secret_here")
