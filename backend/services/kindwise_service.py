import requests
import base64
import os
import json
from pathlib import Path

class KindwiseService:
    """Service to interact with Kindwise crop.health API"""
    
    def __init__(self):
        self.api_key = os.getenv('KINDWISE_API_KEY', '').strip()
        self.api_url = "https://plant.id/api/v3/identification"
        self.pesticide_db_path = Path(__file__).parent.parent / "data" / "pesticide_db.json"
        self.pesticide_db = self._load_pesticide_db()
    
    def _load_pesticide_db(self):
        """Load pesticide database from JSON file"""
        try:
            with open(self.pesticide_db_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Pesticide database not found at {self.pesticide_db_path}")
            return {"diseases": {}}
    
    def _image_to_base64(self, image_path):
        """Convert image file to base64 string"""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _get_auth_headers(self):
        """Return headers for Kindwise auth using the documented Api-Key header."""
        headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            headers['Api-Key'] = self.api_key
        return headers

    def _get_payload(self, image_base64):
        """Build request payload for Kindwise using the documented request format."""
        return {
            'images': [image_base64]
        }
    
    def identify_disease(self, image_path):
        """
        Send image to Kindwise API to identify crop and disease
        
        Args:
            image_path: Path to the image file
            
        Returns:
            dict: Response containing crop name and disease info
        """
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'Kindwise API key is missing. Add KINDWISE_API_KEY to backend/.env and restart the server.'
                }

            # Convert image to base64
            image_base64 = self._image_to_base64(image_path)
            
            # Prepare request headers and payload
            headers = self._get_auth_headers()
            payload = self._get_payload(image_base64)
            
            # Send request to Kindwise API
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            api_response = response.json()
            
            # Extract relevant information from API response
            result = self._parse_kindwise_response(api_response)
            
            return result
            
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_details = e.response.json()
                error_msg = f"{e.response.status_code}: {error_details}"
            except:
                pass

            if e.response is not None and e.response.status_code == 401:
                return {
                    'success': False,
                    'error': 'Kindwise API authentication failed: the API key is invalid, expired, or not authorized for this endpoint. Update KINDWISE_API_KEY in backend/.env with a valid key and restart the server.'
                }

            return {
                'success': False,
                'error': f'API HTTP Error: {error_msg}'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API request failed: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing image: {str(e)}'
            }
    
    def _parse_kindwise_response(self, api_response):
        """
        Parse Kindwise API response and extract crop and disease information
        
        Args:
            api_response: Response from Kindwise API
            
        Returns:
            dict: Parsed disease and crop information
        """
        try:
            print("DEBUG: Raw API Response:")
            print(api_response)
            print("-" * 60)

            result = api_response.get('result', api_response) if isinstance(api_response, dict) else {}
            classification = result.get('classification', {}) if isinstance(result, dict) else {}
            disease_data = result.get('disease', {}) if isinstance(result, dict) else {}

            crop_suggestions = []
            if isinstance(classification, dict):
                crop_suggestions = classification.get('suggestions', [])
            elif isinstance(classification, list):
                crop_suggestions = classification

            disease_suggestions = []
            if isinstance(disease_data, dict):
                disease_suggestions = disease_data.get('suggestions', [])
            elif isinstance(disease_data, list):
                disease_suggestions = disease_data

            crop_name = 'Unknown'
            if crop_suggestions and isinstance(crop_suggestions, list) and len(crop_suggestions) > 0:
                first_crop = crop_suggestions[0]
                if isinstance(first_crop, dict):
                    crop_name = first_crop.get('name', 'Unknown')

            if not crop_name or crop_name == 'Unknown':
                legacy_candidates = []
                if isinstance(result, dict):
                    legacy_candidates = [
                        result.get('crop', {}),
                        result.get('plant', {}),
                        result.get('species', {})
                    ]
                for candidate in legacy_candidates:
                    if isinstance(candidate, dict):
                        suggestions = candidate.get('suggestions', [])
                        if suggestions and isinstance(suggestions, list):
                            crop_name = suggestions[0].get('name', 'Unknown')
                            break

            diseases = []
            if disease_suggestions and isinstance(disease_suggestions, list):
                diseases = disease_suggestions
            elif isinstance(result, dict):
                for key in ['diseases', 'health']:
                    val = result.get(key, [])
                    if isinstance(val, list):
                        diseases = val
                        break
                    if isinstance(val, dict):
                        diseases = val.get('suggestions', [])
                        break

            if not diseases:
                disease_result = {
                    'success': True,
                    'crop': crop_name,
                    'disease': None,
                    'confidence': 0,
                    'raw_response': api_response
                }
            else:
                top_disease = diseases[0]
                disease_name = top_disease.get('name', '') if isinstance(top_disease, dict) else str(top_disease)
                confidence = top_disease.get('probability', 0) if isinstance(top_disease, dict) else 0

                dn = str(disease_name).strip()
                if dn == '' or 'unknown' in dn.lower() or 'healthy' in dn.lower() or 'none' == dn.lower():
                    disease_result = {
                        'success': True,
                        'crop': crop_name,
                        'disease': None,
                        'confidence': 0,
                        'raw_response': api_response
                    }
                else:
                    try:
                        if isinstance(confidence, float) and confidence <= 1.0:
                            conf_str = f'{confidence * 100:.1f}%'
                        else:
                            conf_str = f'{float(confidence):.1f}%'
                    except Exception:
                        conf_str = str(confidence)

                    disease_result = {
                        'success': True,
                        'crop': crop_name,
                        'disease': dn,
                        'confidence': conf_str,
                        'raw_response': api_response
                    }

            print(f"DEBUG: Final result: {disease_result}")
            return disease_result

        except Exception as e:
            print(f"DEBUG: Parse error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'Error parsing API response: {str(e)}'
            }
    
    def get_treatment_recommendations(self, disease_name):
        """
        Get treatment recommendations for a specific disease
        
        Args:
            disease_name: Name of the disease
            
        Returns:
            dict: Treatment information or empty dict if not found
        """
        # Normalize disease name for lookup
        disease_key = disease_name.lower().replace(' ', '_')
        
        # Check in database
        diseases = self.pesticide_db.get('diseases', {})
        
        # Try exact match first
        if disease_key in diseases:
            return diseases[disease_key]
        
        # Try partial match
        for key, value in diseases.items():
            if disease_key in key or key in disease_key:
                return value
        
        # Return healthy if no match found
        return diseases.get('healthy', {
            'crop': 'Unknown',
            'disease_name': disease_name,
            'symptoms': 'Information not available in database',
            'chemical_pesticides': ['Consult local agriculture expert'],
            'organic_treatments': ['Consult local agriculture expert'],
            'prevention': ['Monitor the plant closely']
        })
