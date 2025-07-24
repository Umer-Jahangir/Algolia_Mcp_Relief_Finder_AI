import re
from django.core.management.base import BaseCommand
from disasters.models import disaster_alerts


class Command(BaseCommand):
    help = 'Extract coordinates from existing location and title fields'

    def handle(self, *args, **options):
        # Focus on records that have coordinates in their text but null lat/lon fields
        records = disaster_alerts.objects.filter(
            latitude__isnull=True, 
            longitude__isnull=True
        )
        
        self.stdout.write(f'Processing {records.count()} records without coordinates...')
        
        updated_count = 0
        
        for record in records:
            # Check location field first
            lat, lon = self.extract_from_text(record.location)
            
            # If not found in location, check title
            if lat is None and lon is None:
                lat, lon = self.extract_from_text(record.title)
            
            if lat is not None and lon is not None:
                record.latitude = lat
                record.longitude = lon
                record.save()
                updated_count += 1
                
                self.stdout.write(
                    f'Updated ID {record.id}: {record.title[:40]}... '
                    f'-> ({lat}, {lon})'
                )
        
        # Final stats
        total_with_coords = disaster_alerts.objects.filter(
            latitude__isnull=False, 
            longitude__isnull=False
        ).count()
        total_records = disaster_alerts.objects.count()
        
        self.stdout.write(self.style.SUCCESS(
            f'\nCoordinate extraction completed!\n'
            f'Updated: {updated_count} records\n'
            f'Total with coordinates: {total_with_coords}/{total_records} '
            f'({total_with_coords/total_records*100:.1f}%)'
        ))

    def extract_from_text(self, text):
        """Extract coordinates from text using multiple patterns"""
        if not text:
            return None, None
        
        # Pattern 1: Coordinates in parentheses like "(-6.08, 142.66)"
        pattern1 = r'\((-?\d+\.?\d*),\s*(-?\d+\.?\d*)\)'
        match = re.search(pattern1, text)
        if match:
            try:
                return float(match.group(1)), float(match.group(2))
            except ValueError:
                pass
        
        # Pattern 2: Coordinates without parentheses like "-6.08, 142.66"
        pattern2 = r'(-?\d+\.?\d+),\s*(-?\d+\.?\d+)'
        match = re.search(pattern2, text)
        if match:
            try:
                lat, lon = float(match.group(1)), float(match.group(2))
                # Basic validation - rough bounds check
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return lat, lon
            except ValueError:
                pass
        
        return None, None


class Command(BaseCommand):
    help = 'Extract and populate missing data from existing disaster records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--coords-only', 
            action='store_true',
            help='Only extract coordinates'
        )
        parser.add_argument(
            '--time-only', 
            action='store_true',
            help='Only extract disaster times'
        )
        parser.add_argument(
            '--show-examples', 
            action='store_true',
            help='Show examples of data that would be extracted'
        )

    def handle(self, *args, **options):
        if options['show_examples']:
            self.show_examples()
            return
        
        if options['coords_only']:
            self.fix_coordinates()
        elif options['time_only']:
            self.fix_disaster_times()
        else:
            self.fix_all_data()

    def show_examples(self):
        """Show examples of what data can be extracted"""
        self.stdout.write("=== COORDINATE EXTRACTION EXAMPLES ===")
        
        # Find records with coordinates in text but null in fields
        examples = disaster_alerts.objects.filter(
            latitude__isnull=True, 
            longitude__isnull=True
        )[:10]
        
        for record in examples:
            lat, lon = self.extract_coordinates(record.location, record.title)
            if lat is not None and lon is not None:
                self.stdout.write(f"ID {record.id}: {record.title}")
                self.stdout.write(f"  Location: {record.location}")
                self.stdout.write(f"  Would extract: ({lat}, {lon})\n")
        
        self.stdout.write("=== TIME EXTRACTION EXAMPLES ===")
        
        # Find records with dates in text but null in fields
        time_examples = disaster_alerts.objects.filter(disaster_time__isnull=True)[:5]
        
        for record in time_examples:
            disaster_time = self.extract_disaster_time(record.description, record.title)
            if disaster_time:
                self.stdout.write(f"ID {record.id}: {record.title}")
                self.stdout.write(f"  Description: {record.description[:100]}...")
                self.stdout.write(f"  Would extract: {disaster_time}\n")

    def fix_coordinates(self):
        """Fix only coordinates"""
        records = disaster_alerts.objects.filter(
            latitude__isnull=True, 
            longitude__isnull=True
        )
        
        self.stdout.write(f'Fixing coordinates for {records.count()} records...')
        updated = 0
        
        for record in records:
            lat, lon = self.extract_coordinates(record.location, record.title)
            if lat is not None and lon is not None:
                record.latitude = lat
                record.longitude = lon
                record.save()
                updated += 1
                self.stdout.write(f'✓ Updated coordinates for: {record.title[:50]}')
        
        self.stdout.write(self.style.SUCCESS(f'Updated coordinates for {updated} records'))

    def fix_disaster_times(self):
        """Fix only disaster times"""
        records = disaster_alerts.objects.filter(disaster_time__isnull=True)
        
        self.stdout.write(f'Fixing disaster times for {records.count()} records...')
        updated = 0
        
        for record in records:
            disaster_time = self.extract_disaster_time(record.description, record.title)
            if disaster_time:
                record.disaster_time = disaster_time
                record.save()
                updated += 1
                self.stdout.write(f'✓ Updated time for: {record.title[:50]}')
        
        self.stdout.write(self.style.SUCCESS(f'Updated disaster times for {updated} records'))

    def fix_all_data(self):
        """Fix all missing data"""
        records = disaster_alerts.objects.all()
        
        self.stdout.write(f'Enhancing all {records.count()} records...')
        
        stats = {
            'coords': 0,
            'times': 0, 
            'population': 0,
            'types': 0
        }
        
        for record in records:
            updated = False
            
            #  coordinates
            if record.latitude is None or record.longitude is None:
                lat, lon = self.extract_coordinates(record.location, record.title)
                if lat is not None and lon is not None:
                    record.latitude = lat
                    record.longitude = lon
                    stats['coords'] += 1
                    updated = True
            
            #  disaster time
            if record.disaster_time is None:
                disaster_time = self.extract_disaster_time(record.description, record.title)
                if disaster_time:
                    record.disaster_time = disaster_time
                    stats['times'] += 1
                    updated = True
            
            #  population
            if record.population_affected == 0:
                population = self.extract_population(record.description, record.title)
                if population > 0:
                    record.population_affected = population
                    stats['population'] += 1
                    updated = True
            
            #  disaster type
            if record.disaster_type in ['Unknown', '', None]:
                disaster_type = self.determine_disaster_type(record.title, record.description)
                if disaster_type != 'Unknown':
                    record.disaster_type = disaster_type
                    stats['types'] += 1
                    updated = True
            
            if updated:
                record.save()
        
        # Final summary
        total = records.count()
        final_coords = disaster_alerts.objects.filter(latitude__isnull=False, longitude__isnull=False).count()
        final_times = disaster_alerts.objects.filter(disaster_time__isnull=False).count()
        final_population = disaster_alerts.objects.filter(population_affected__gt=0).count()
        final_types = disaster_alerts.objects.exclude(disaster_type__in=['Unknown', '', None]).count()
        
        self.stdout.write(self.style.SUCCESS(
            f'\n=== ENHANCEMENT COMPLETED ===\n'
            f'Coordinates updated: {stats["coords"]} records\n'
            f'Times updated: {stats["times"]} records\n'
            f'Population updated: {stats["population"]} records\n'
            f'Types updated: {stats["types"]} records\n\n'
            f'=== FINAL DATA QUALITY ===\n'
            f'Coordinates: {final_coords}/{total} ({final_coords/total*100:.1f}%)\n'
            f'Times: {final_times}/{total} ({final_times/total*100:.1f}%)\n'
            f'Population: {final_population}/{total} ({final_population/total*100:.1f}%)\n'
            f'Types: {final_types}/{total} ({final_types/total*100:.1f}%)'
        ))

    def extract_coordinates(self, location, title):
        """Extract coordinates from location or title"""
        text = f"{location or ''} {title or ''}"
        
        # Your Papua New Guinea example: "41 km SW of Tari, Papua New Guinea (-6.08, 142.66)"
        pattern = r'\((-?\d+\.?\d*),\s*(-?\d+\.?\d*)\)'
        match = re.search(pattern, text)
        if match:
            try:
                lat, lon = float(match.group(1)), float(match.group(2))
                # Basic validation
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return lat, lon
            except ValueError:
                pass
        
        return None, None

    def extract_disaster_time(self, description, title):
        """Extract disaster time from description or title"""
        from datetime import datetime
        from django.utils import timezone
        
        text = f"{description or ''} {title or ''}"
        
        #  example of show dates like "17/07/2025 09:04 UTC" and "7/17/2025 9:04:23 AM"
        patterns = [
            (r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})\s+UTC', '%d/%m/%Y %H:%M'),
            (r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}:\d{2})\s+(AM|PM)', '%m/%d/%Y %I:%M:%S %p'),
            (r'On\s+(\d{1,2}/\d{1,2}/\d{4})', '%d/%m/%Y'),
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
                    return timezone.make_aware(dt)
                except ValueError:
                    continue
        
        return None

    def extract_population(self, description, title):
        """Extract population from text"""
        text = f"{description or ''} {title or ''}".lower()
        
        patterns = [
            (r'(\d+(?:\.\d+)?)\s+million', 1000000),
            (r'(\d+(?:,\d+)*)\s+thousand', 1000),
            (r'(\d+(?:,\d+)*)\s+displaced', 1),
            (r'(\d+(?:,\d+)*)\s+deaths', 1),
        ]
        
        max_pop = 0
        for pattern, multiplier in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    num = int(str(match).replace(',', '')) * multiplier
                    max_pop = max(max_pop, num)
                except ValueError:
                    continue
        
        return max_pop

    def determine_disaster_type(self, title, description):
        """Determine disaster type"""
        text = f"{title or ''} {description or ''}".lower()
        
        types = {
            'EQ': ['earthquake', 'magnitude', 'seismic'],
            'FL': ['flood', 'flooding'],
            'WF': ['forest fire', 'fire'],
            'TC': ['cyclone', 'tropical'],
            'VO': ['volcanic', 'volcano'],
        }
        
        for disaster_type, keywords in types.items():
            if any(keyword in text for keyword in keywords):
                return disaster_type
        
        return 'Unknown'