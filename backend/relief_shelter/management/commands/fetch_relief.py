import requests
import json
from datetime import datetime, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from relief_shelter.models import Relief_Shelter

class Command(BaseCommand):
    help = "Fetch Pakistani relief center data and update Relief_Shelter model with comprehensive information"

    # Pakistani Relief Center APIs and Data Sources
    PAKISTANI_APIS = {
        # HDX Humanitarian Data Exchange for Pakistan
        'hdx_pakistan': 'https://data.humdata.org/api/3/action/package_search?q=pakistan+shelter+relief',
        'hdx_facilities': 'https://data.humdata.org/api/3/action/datastore_search?resource_id=facilities-pakistan',
        
        # Open Data Pakistan sources
        'opendata_pk': 'https://opendata.com.pk/api/3/action/package_search?q=relief+shelter',
        'opendata_facilities': 'https://opendata.com.pk/api/3/action/package_search?q=emergency+services',
        
        # KP Open Data Portal
        'kp_opendata': 'https://opendata.kp.gov.pk/api/3/action/package_search?q=relief+centers',
        'kp_health_facilities': 'https://opendata.kp.gov.pk/api/3/action/package_search?q=health+facilities',
        
        # ReliefWeb API for Pakistan
        'reliefweb_pak': 'https://api.reliefweb.int/v1/reports?appname=your-app&query[value]=pakistan+relief+centers&query[operator]=AND',
        
        # World Bank Open Data for Pakistan facilities
        'worldbank_pak': 'https://api.worldbank.org/v2/country/pak/indicator?format=json',
        
        # OCHA Services (UN Office for the Coordination of Humanitarian Affairs)
        'ocha_pak': 'https://api.hpc.tools/v2/public/plan/country/pak',
        
        # Custom APIs for Pakistani Relief Centers (Mock URLs - replace with actual APIs when available)
        'ndma_relief_centers': 'https://ndma.gov.pk/api/relief-centers',  # Mock - replace with actual
        'pdma_punjab': 'https://pdma.punjab.gov.pk/api/shelters',  # Mock
        'pdma_sindh': 'https://pdma.gos.pk/api/relief-camps',  # Mock
        'pdma_kp': 'https://pdma.kp.gov.pk/api/emergency-shelters',  # Mock
        'pdma_balochistan': 'https://pdma.gob.pk/api/disaster-relief',  # Mock
        
        # NGO and Humanitarian Organization APIs
        'edhi_foundation': 'https://edhi.org/api/centers',  # Mock
        'akhuwat_foundation': 'https://akhuwat.org.pk/api/relief-centers',  # Mock
        'jdc_pakistan': 'https://jdcpakistan.com/api/emergency-response',  # Mock
    }

    # DC API for comparison (original)
    DC_API_URL = (
        "https://opendata.dc.gov/api/download/v1/"
        "items/87c5e68942304363a4578b30853f385d/geojson?layers=25"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            default='all',
            help='Data source: all, pakistan, dc (default: all)',
        )
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Force update all records even if they exist',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )
        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Run in test mode with sample data',
        )

    def handle(self, *args, **options):
        self.verbose = options.get('verbose', False)
        self.force_update = options.get('force_update', False)
        self.source = options.get('source', 'all')
        self.test_mode = options.get('test_mode', False)
        
        self.stdout.write(self.style.SUCCESS(f"Starting relief center data fetch from: {self.source}"))
        
        total_added = total_updated = total_skipped = 0
        
        if self.test_mode:
            # Add sample Pakistani data for testing
            added, updated, skipped = self.process_sample_data()
            total_added += added
            total_updated += updated
            total_skipped += skipped
        
        if self.source in ['all', 'pakistan']:
            # Fetch Pakistani relief center data
            added, updated, skipped = self.fetch_pakistani_data()
            total_added += added
            total_updated += updated
            total_skipped += skipped
        
        if self.source in ['all', 'dc']:
            # Fetch DC data (original functionality)
            added, updated, skipped = self.fetch_dc_data()
            total_added += added
            total_updated += updated
            total_skipped += skipped
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Total Results - Added: {total_added}, Updated: {total_updated}, Skipped: {total_skipped}"
            )
        )

    def fetch_pakistani_data(self):
        """Fetch data from Pakistani sources"""
        self.stdout.write("Fetching Pakistani relief center data...")
        
        all_data = []
        working_apis = 0
        
        for source_name, api_url in self.PAKISTANI_APIS.items():
            try:
                if self.verbose:
                    self.stdout.write(f"  Trying {source_name}...")
                
                # Skip mock APIs in production (they don't exist yet)
                if any(mock in api_url for mock in ['ndma.gov.pk/api', 'pdma.', 'edhi.org/api', 'akhuwat.org.pk/api']):
                    if self.verbose:
                        self.stdout.write(f"    Skipping mock API: {source_name}")
                    continue
                
                headers = {
                    'User-Agent': 'Relief-Shelter-App/1.0',
                    'Accept': 'application/json'
                }
                
                response = requests.get(api_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Process different API response formats
                    processed_data = self.process_api_response(data, source_name)
                    if processed_data:
                        all_data.extend(processed_data)
                        working_apis += 1
                        if self.verbose:
                            self.stdout.write(f"    ✓ {source_name}: {len(processed_data)} records")
                    
                elif response.status_code == 404:
                    if self.verbose:
                        self.stdout.write(f"    - {source_name}: No data available (404)")
                else:
                    if self.verbose:
                        self.stdout.write(f"    - {source_name}: HTTP {response.status_code}")
                        
            except requests.exceptions.Timeout:
                if self.verbose:
                    self.stdout.write(f"    - {source_name}: Timeout")
            except requests.exceptions.RequestException as e:
                if self.verbose:
                    self.stdout.write(f"    - {source_name}: Connection error")
            except json.JSONDecodeError:
                if self.verbose:
                    self.stdout.write(f"    - {source_name}: Invalid JSON response")
            except Exception as e:
                if self.verbose:
                    self.stdout.write(f"    - {source_name}: Error - {str(e)}")
        
        self.stdout.write(f"Successfully connected to {working_apis} Pakistani data sources")
        self.stdout.write(f"Found {len(all_data)} relief center records from Pakistani sources")
        
        # If no real data found, use sample data for demonstration
        if not all_data and not self.test_mode:
            self.stdout.write(self.style.WARNING("No data from Pakistani APIs, using sample data for demonstration"))
            return self.process_sample_data()
        
        return self.process_relief_data(all_data, 'Pakistani')

    def process_api_response(self, data, source_name):
        """Process different API response formats"""
        processed = []
        
        try:
            # HDX API format
            if source_name.startswith('hdx'):
                if 'result' in data and 'records' in data['result']:
                    for record in data['result']['records']:
                        processed.append(self.normalize_hdx_data(record))
                elif 'result' in data and 'results' in data['result']:
                    for result in data['result']['results']:
                        if 'resources' in result:
                            for resource in result['resources']:
                                processed.append(self.normalize_hdx_data(resource))
            
            # Open Data Pakistan format
            elif source_name.startswith('opendata') or source_name.startswith('kp'):
                if 'result' in data and 'results' in data['result']:
                    for result in data['result']['results']:
                        processed.append(self.normalize_opendata_pk(result))
            
            # ReliefWeb format
            elif source_name == 'reliefweb_pak':
                if 'data' in data:
                    for item in data['data']:
                        processed.append(self.normalize_reliefweb_data(item))
            
            # OCHA format
            elif source_name == 'ocha_pak':
                if 'data' in data:
                    processed.append(self.normalize_ocha_data(data['data']))
            
            # Generic format
            else:
                if isinstance(data, list):
                    for item in data:
                        processed.append(self.normalize_generic_data(item))
                elif isinstance(data, dict) and 'features' in data:
                    for feature in data['features']:
                        processed.append(self.normalize_geojson_data(feature))
                        
        except Exception as e:
            if self.verbose:
                self.stdout.write(f"Error processing {source_name}: {str(e)}")
        
        return processed

    def normalize_hdx_data(self, record):
        """Normalize HDX data format to standard format"""
        return {
            'name': record.get('name', 'Unknown Facility'),
            'address': f"{record.get('city', '')}, {record.get('admin1', '')}, Pakistan".strip(', '),
            'latitude': float(record.get('latitude', 0)) if record.get('latitude') else 31.5204,  # Lahore default
            'longitude': float(record.get('longitude', 0)) if record.get('longitude') else 74.3587,
            'phone_number': record.get('phone', ''),
            'source': 'HDX Pakistan',
            'has_bed': True,  # Assume shelters have beds
            'has_food': record.get('services', '').lower().find('food') != -1,
            'has_water': True,  # Basic necessity
            'has_medical': record.get('services', '').lower().find('medical') != -1,
            'is_open': record.get('status', '').lower() != 'closed',
        }

    def normalize_opendata_pk(self, record):
        """Normalize Open Data Pakistan format"""
        return {
            'name': record.get('title', 'Relief Center'),
            'address': record.get('notes', '').split('\n')[0] if record.get('notes') else 'Pakistan',
            'latitude': 31.5204,  # Default coordinates for Pakistan
            'longitude': 74.3587,
            'phone_number': '',
            'source': 'Open Data Pakistan',
            'website': record.get('url', ''),
            'has_bed': True,
            'has_food': True,
            'has_water': True,
            'has_medical': False,
            'is_open': True,
        }

    def normalize_reliefweb_data(self, record):
        """Normalize ReliefWeb data format"""
        fields = record.get('fields', {})
        return {
            'name': fields.get('title', 'Relief Center'),
            'address': f"{fields.get('country', {}).get('name', 'Pakistan')}",
            'latitude': 31.5204,
            'longitude': 74.3587,
            'phone_number': '',
            'source': 'ReliefWeb',
            'website': fields.get('url', ''),
            'has_bed': True,
            'has_food': True,
            'has_water': True,
            'has_medical': True,
            'is_open': True,
        }

    def normalize_ocha_data(self, record):
        """Normalize OCHA data format"""
        return {
            'name': record.get('name', 'OCHA Relief Center'),
            'address': 'Pakistan',
            'latitude': 31.5204,
            'longitude': 74.3587,
            'phone_number': '',
            'source': 'OCHA',
            'has_bed': True,
            'has_food': True,
            'has_water': True,
            'has_medical': True,
            'is_open': True,
        }

    def normalize_generic_data(self, record):
        """Normalize generic data format"""
        return {
            'name': record.get('name', record.get('title', 'Relief Center')),
            'address': record.get('address', record.get('location', 'Pakistan')),
            'latitude': float(record.get('lat', record.get('latitude', 31.5204))),
            'longitude': float(record.get('lng', record.get('longitude', 74.3587))),
            'phone_number': record.get('phone', record.get('contact', '')),
            'source': 'Generic API',
            'has_bed': record.get('beds', True),
            'has_food': record.get('food', True),
            'has_water': record.get('water', True),
            'has_medical': record.get('medical', False),
            'is_open': record.get('open', True),
        }

    def normalize_geojson_data(self, feature):
        """Normalize GeoJSON data format"""
        props = feature.get('properties', {})
        coords = feature.get('geometry', {}).get('coordinates', [74.3587, 31.5204])
        
        return {
            'name': props.get('name', props.get('NAME', 'Relief Center')),
            'address': props.get('address', props.get('ADDRESS', 'Pakistan')),
            'latitude': float(coords[1]) if len(coords) > 1 else 31.5204,
            'longitude': float(coords[0]) if len(coords) > 0 else 74.3587,
            'phone_number': props.get('phone', props.get('PHONE', '')),
            'source': 'GeoJSON Data',
            'has_bed': props.get('beds', True),
            'has_food': props.get('food', True),
            'has_water': props.get('water', True),
            'has_medical': props.get('medical', False),
            'is_open': props.get('open', True),
        }

    def process_sample_data(self):
        """Process sample Pakistani relief center data for testing"""
        sample_data = [
            {
                'name': 'Edhi Foundation Emergency Shelter - Karachi',
                'address': 'Mithadar, Karachi, Sindh, Pakistan',
                'latitude': 24.8615, 'longitude': 67.0099,
                'phone_number': '(021) 111-113-344',
                'email': 'info@edhi.org', 'website': 'https://edhi.org',
                'has_bed': True, 'has_food': True, 'has_water': True,
                'has_medical': True, 'has_shower': True, 'has_laundry': False,
                'is_24_7': True, 'wheelchair_accessible': False,
                'accepts_families': True, 'accepts_men': True, 'accepts_women': True,
                'accepts_pets': False, 'has_case_management': False,
                'has_mental_health': False, 'has_substance_abuse': False,
                'is_open': True, 'is_emergency': True,
                'total_spaces': 200, 'available_spaces': 180,
                'source': 'Edhi Foundation'
            },
            {
                'name': 'PDMA Punjab Relief Camp - Lahore',
                'address': 'Township, Lahore, Punjab, Pakistan',
                'latitude': 31.5204, 'longitude': 74.3587,
                'phone_number': '(042) 111-222-333',
                'email': 'info@pdma.punjab.gov.pk', 'website': 'https://pdma.punjab.gov.pk',
                'has_bed': True, 'has_food': True, 'has_water': True,
                'has_medical': True, 'has_shower': True, 'has_laundry': True,
                'is_24_7': True, 'wheelchair_accessible': True,
                'accepts_families': True, 'accepts_men': True, 'accepts_women': True,
                'accepts_pets': False, 'has_case_management': True,
                'has_mental_health': True, 'has_substance_abuse': False,
                'is_open': True, 'is_emergency': False,
                'total_spaces': 500, 'available_spaces': 350,
                'hours_open': time(6, 0), 'hours_close': time(22, 0),
                'source': 'PDMA Punjab'
            },
            {
                'name': 'Akhuwat Relief Center - Islamabad',
                'address': 'F-7 Markaz, Islamabad, Pakistan',
                'latitude': 33.6844, 'longitude': 73.0479,
                'phone_number': '(051) 111-253-482',
                'email': 'info@akhuwat.org.pk', 'website': 'https://akhuwat.org.pk',
                'has_bed': True, 'has_food': True, 'has_water': True,
                'has_medical': False, 'has_shower': True, 'has_laundry': False,
                'is_24_7': False, 'wheelchair_accessible': True,
                'accepts_families': True, 'accepts_men': True, 'accepts_women': True,
                'accepts_pets': False, 'has_case_management': True,
                'has_mental_health': False, 'has_substance_abuse': False,
                'is_open': True, 'is_emergency': False,
                'total_spaces': 100, 'available_spaces': 85,
                'hours_open': time(8, 0), 'hours_close': time(20, 0),
                'source': 'Akhuwat Foundation'
            },
            {
                'name': 'JDC Emergency Response Center - Peshawar',
                'address': 'University Town, Peshawar, KPK, Pakistan',
                'latitude': 34.0151, 'longitude': 71.5249,
                'phone_number': '(091) 111-532-532',
                'email': 'info@jdcpakistan.com', 'website': 'https://jdcpakistan.com',
                'has_bed': True, 'has_food': True, 'has_water': True,
                'has_medical': True, 'has_shower': False, 'has_laundry': False,
                'is_24_7': True, 'wheelchair_accessible': False,
                'accepts_families': True, 'accepts_men': True, 'accepts_women': True,
                'accepts_pets': False, 'has_case_management': False,
                'has_mental_health': False, 'has_substance_abuse': False,
                'is_open': True, 'is_emergency': True,
                'total_spaces': 150, 'available_spaces': 120,
                'source': 'JDC Pakistan'
            },
            {
                'name': 'PDMA Balochistan Relief Shelter - Quetta',
                'address': 'Cantt Area, Quetta, Balochistan, Pakistan',
                'latitude': 30.1798, 'longitude': 66.9750,
                'phone_number': '(081) 111-444-555',
                'email': 'info@pdma.gob.pk', 'website': 'https://pdma.gob.pk',
                'has_bed': True, 'has_food': True, 'has_water': True,
                'has_medical': True, 'has_shower': True, 'has_laundry': True,
                'is_24_7': False, 'wheelchair_accessible': False,
                'accepts_families': True, 'accepts_men': True, 'accepts_women': True,
                'accepts_pets': False, 'has_case_management': True,
                'has_mental_health': False, 'has_substance_abuse': False,
                'is_open': True, 'is_emergency': False,
                'total_spaces': 300, 'available_spaces': 250,
                'hours_open': time(7, 0), 'hours_close': time(21, 0),
                'source': 'PDMA Balochistan'
            }
        ]
        
        return self.process_relief_data(sample_data, 'Pakistani Sample')

    def fetch_dc_data(self):
        """Fetch DC data (original functionality)"""
        try:
            self.stdout.write("Fetching DC shelter data...")
            resp = requests.get(self.DC_API_URL, timeout=10)
            resp.raise_for_status()
            
            data = resp.json()
            dc_data = []
            
            for feature in data.get("features", []):
                normalized = self.normalize_dc_data(feature)
                if normalized:
                    dc_data.append(normalized)
            
            return self.process_relief_data(dc_data, 'DC')
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error fetching DC data: {e}"))
            return 0, 0, 0

    def normalize_dc_data(self, feature):
        """Normalize DC data to standard format"""
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [None, None])
        if not props or None in coords:
            return None

        name = props.get("FacilityName") or props.get("Name", "Unnamed Shelter")
        address = props.get("Address", "No Address")
        phone = props.get("Phone", "")

        lat, lng = coords[1], coords[0]

        return {
            'name': name,
            'address': address,
            'latitude': float(lat),
            'longitude': float(lng),
            'phone_number': phone,
            'source': 'DC Open Data',
            'has_bed': bool(props.get("Beds", 0)),
            'has_food': bool(props.get("Food")),
            'has_water': bool(props.get("Water")),
            'has_medical': False,
            'is_24_7': bool(props.get("Open_24x7", 0)),
            'is_open': True,
            'total_spaces': props.get("Beds", 0),
            'available_spaces': props.get("AvailableBeds", props.get("Beds", 0)),
        }

    def process_relief_data(self, data_list, source_name):
        """Process relief center data and update database"""
        added = updated = skipped = 0
        
        for relief_data in data_list:
            try:
                # Ensure all required fields have default values
                relief_data = self.ensure_complete_data(relief_data)
                
                # Use name and address as unique identifiers
                lookup_fields = {
                    'name': relief_data['name'],
                    'address': relief_data['address']
                }
                
                if self.force_update:
                    Relief_Shelter.objects.filter(**lookup_fields).delete()
                    obj = Relief_Shelter.objects.create(**relief_data)
                    created = True
                else:
                    obj, created = Relief_Shelter.objects.update_or_create(
                        **lookup_fields,
                        defaults=relief_data
                    )

                if created:
                    added += 1
                    if self.verbose:
                        self.stdout.write(f"  Added: {relief_data['name']}")
                else:
                    updated += 1
                    if self.verbose:
                        self.stdout.write(f"  Updated: {relief_data['name']}")

            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Error processing {relief_data.get('name', 'Unknown')}: {e}")
                )
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{source_name} - Added: {added}, Updated: {updated}, Skipped: {skipped}"
            )
        )
        
        return added, updated, skipped

    def ensure_complete_data(self, data):
        """Ensure all Relief_Shelter fields have appropriate default values"""
        defaults = {
            'name': 'Unknown Relief Center',
            'address': 'Pakistan',
            'latitude': 31.5204,  # Pakistan center
            'longitude': 74.3587,
            'phone_number': '',
            'email': '',
            'website': '',
            'has_bed': True,
            'has_food': True,
            'has_water': True,
            'has_medical': False,
            'has_shower': False,
            'has_laundry': False,
            'is_24_7': False,
            'hours_open': None,
            'hours_close': None,
            'wheelchair_accessible': False,
            'accepts_families': True,
            'accepts_men': True,
            'accepts_women': True,
            'accepts_pets': False,
            'has_case_management': False,
            'has_mental_health': False,
            'has_substance_abuse': False,
            'is_open': True,
            'is_emergency': False,
            'total_spaces': 0,
            'available_spaces': 0,
            'distance': 0.0,
            'source': 'Unknown',
            'last_updated': timezone.now(),
        }
        
        # Merge with provided data
        for key, default_value in defaults.items():
            if key not in data or data[key] is None:
                data[key] = default_value
        
        return data