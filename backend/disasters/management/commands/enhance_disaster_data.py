import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from disasters.models import disaster_alerts
from algoliasearch_django.decorators import disable_auto_indexing


class Command(BaseCommand):
    help = 'Enhance existing disaster records by extracting missing data from titles and descriptions'

    def handle(self, *args, **options):
        with disable_auto_indexing():
            # Get all records
            records = disaster_alerts.objects.all()
            self.stdout.write(f'Processing {records.count()} records...')
            
            updated_coords = 0
            updated_time = 0
            updated_population = 0
            updated_type = 0
            
            for record in records:
                updated = False
                original_record = f"ID {record.id}: {record.title[:50]}..."
                
                # 1. Extract coordinates from location or title
                if record.latitude is None or record.longitude is None:
                    lat, lon = self.extract_coordinates(record.location, record.title)
                    if lat is not None and lon is not None:
                        record.latitude = lat
                        record.longitude = lon
                        updated = True
                        updated_coords += 1
                        self.stdout.write(f'Added coords to {original_record}: ({lat}, {lon})')
                
                # 2. Extract disaster time from description or title
                if record.disaster_time is None:
                    disaster_time = self.extract_disaster_time(record.description, record.title)
                    if disaster_time:
                        record.disaster_time = disaster_time
                        updated = True
                        updated_time += 1
                        self.stdout.write(f'Added time to {original_record}: {disaster_time}')
                
                # 3. Extract population from description
                if record.population_affected == 0:
                    population = self.extract_population(record.description, record.title)
                    if population > 0:
                        record.population_affected = population
                        updated = True
                        updated_population += 1
                        self.stdout.write(f'Added population to {original_record}: {population}')
                
                # 4. Determine disaster type
                if record.disaster_type in ['Unknown', '', None]:
                    disaster_type = self.determine_disaster_type(record.title, record.description)
                    if disaster_type and disaster_type != 'Unknown':
                        record.disaster_type = disaster_type
                        updated = True
                        updated_type += 1
                        self.stdout.write(f'Added type to {original_record}: {disaster_type}')
                
                if updated:
                    record.save()
            
            # Final summary
            total = records.count()
            final_coords = disaster_alerts.objects.filter(latitude__isnull=False, longitude__isnull=False).count()
            final_time = disaster_alerts.objects.filter(disaster_time__isnull=False).count()
            final_population = disaster_alerts.objects.filter(population_affected__gt=0).count()
            final_type = disaster_alerts.objects.exclude(disaster_type__in=['Unknown', '', None]).count()
            
            self.stdout.write(self.style.SUCCESS(
                f'\nEnhancement Results:\n'
                f'Updated coordinates: {updated_coords} records\n'
                f'Updated disaster time: {updated_time} records\n'
                f'Updated population: {updated_population} records\n'
                f'Updated disaster type: {updated_type} records\n\n'
                f'Final Data Quality:\n'
                f'Records with coordinates: {final_coords}/{total} ({final_coords/total*100:.1f}%)\n'
                f'Records with disaster time: {final_time}/{total} ({final_time/total*100:.1f}%)\n'
                f'Records with population: {final_population}/{total} ({final_population/total*100:.1f}%)\n'
                f'Records with disaster type: {final_type}/{total} ({final_type/total*100:.1f}%)'
            ))

    def extract_coordinates(self, location, title):
        """Extract latitude and longitude from location string or title"""
        text = f"{location or ''} {title or ''}"
        
        # Pattern 1: Coordinates in parentheses like (-6.08, 142.66)
        coord_pattern1 = r'\((-?\d+\.?\d*),\s*(-?\d+\.?\d*)\)'
        match = re.search(coord_pattern1, text)
        if match:
            try:
                return float(match.group(1)), float(match.group(2))
            except ValueError:
                pass
        
        # Pattern 2: Coordinates after location like "Papua New Guinea -6.08, 142.66"
        coord_pattern2 = r'(-?\d+\.?\d+),\s*(-?\d+\.?\d+)'
        match = re.search(coord_pattern2, text)
        if match:
            try:
                return float(match.group(1)), float(match.group(2))
            except ValueError:
                pass
        
        # Pattern 3: Individual lat/lon mentions
        lat_pattern = r'lat(?:itude)?[:\s]*(-?\d+\.?\d*)'
        lon_pattern = r'lon(?:gitude)?[:\s]*(-?\d+\.?\d*)'
        
        lat_match = re.search(lat_pattern, text, re.IGNORECASE)
        lon_match = re.search(lon_pattern, text, re.IGNORECASE)
        
        if lat_match and lon_match:
            try:
                return float(lat_match.group(1)), float(lon_match.group(1))
            except ValueError:
                pass
        
        return None, None
    
    def extract_disaster_time(self, description, title):
        """Extract disaster time from description or title"""
        text = f"{description or ''} {title or ''}"
        
        # Multiple date patterns
        patterns = [
            # Pattern: "17/07/2025 09:04 UTC" or "16/07/2025 20:37 UTC"
            (r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})\s+UTC', '%d/%m/%Y %H:%M'),
            # Pattern: "7/17/2025 9:04:23 AM"
            (r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}:\d{2})\s+(AM|PM)', '%m/%d/%Y %I:%M:%S %p'),
            # Pattern: "On 7/17/2025 9:04:23 AM"
            (r'On\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}:\d{2})\s+(AM|PM)', '%m/%d/%Y %I:%M:%S %p'),
            # Pattern: "On 14/07/2025"
            (r'On\s+(\d{1,2}/\d{1,2}/\d{4})', '%d/%m/%Y'),
            # Pattern: "From 17/07/2025"
            (r'From\s+(\d{1,2}/\d{1,2}/\d{4})', '%d/%m/%Y'),
            # Pattern: ISO format "2025-07-17T16:25:52"
            (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', '%Y-%m-%dT%H:%M:%S'),
            # Pattern: "2025-07-17"
            (r'(\d{4}-\d{2}-\d{2})', '%Y-%m-%d'),
        ]
        
        for pattern, date_format in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    if isinstance(match, tuple):
                        if len(match) == 3:  # Date, time, AM/PM
                            date_str = f"{match[0]} {match[1]} {match[2]}"
                        elif len(match) == 2:  # Date and time
                            date_str = f"{match[0]} {match[1]}"
                        else:
                            date_str = match[0]
                    else:
                        date_str = match
                    
                    dt = datetime.strptime(date_str, date_format)
                    return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def extract_population(self, description, title):
        """Extract population affected from text"""
        text = f"{description or ''} {title or ''}".lower()
        
        max_population = 0
        
        # Pattern 1: "580 thousand" or "40.119 million"
        patterns = [
            (r'(\d+(?:\.\d+)?)\s+million', 1000000),
            (r'(\d+(?:,\d+)*)\s+thousand', 1000),
            # Pattern 2: "affecting 580 thousand"
            (r'affecting\s+(\d+(?:,\d+)*)\s+thousand', 1000),
            (r'affecting\s+(\d+(?:\.\d+)?)\s+million', 1000000),
            # Pattern 3: Direct numbers with context
            (r'(\d+(?:,\d+)*)\s+displaced', 1),
            (r'(\d+(?:,\d+)*)\s+deaths', 1),
            (r'(\d+(?:,\d+)*)\s+in\s+mmi', 1),
            (r'population\s+affected.*?(\d+(?:,\d+)*)', 1),
        ]
        
        for pattern, multiplier in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    # Remove commas and convert
                    num_str = str(match).replace(',', '')
                    population = int(float(num_str) * multiplier)
                    max_population = max(max_population, population)
                except (ValueError, TypeError):
                    continue
        
        return max_population
    
    def determine_disaster_type(self, title, description):
        """Determine disaster type from title and description"""
        text = f"{title or ''} {description or ''}".lower()
        
        # Disaster type mapping with keywords
        disaster_types = {
            'EQ': ['earthquake', 'magnitude', 'seismic', 'tremor', 'quake'],
            'FL': ['flood', 'flooding', 'inundation', 'overflow'],
            'WF': ['forest fire', 'wildfire', 'fire alert', 'bushfire', 'fire'],
            'TC': ['cyclone', 'hurricane', 'typhoon', 'tropical storm', 'tropical depression'],
            'VO': ['volcanic', 'eruption', 'volcano', 'ash cloud', 'lava'],
            'DR': ['drought', 'dry spell', 'water shortage'],
            'LS': ['landslide', 'mudslide', 'slope failure'],
            'TS': ['tsunami', 'tidal wave', 'seismic wave'],
        }
        
        # Score each disaster type
        scores = {}
        for disaster_type, keywords in disaster_types.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[disaster_type] = score
        
        # Return the disaster type with highest score
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return 'Unknown'