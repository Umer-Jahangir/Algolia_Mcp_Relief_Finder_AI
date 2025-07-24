# disasters/index.py - Corrected version with proper datetime handling
from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register
from .models import disaster_alerts

@register(disaster_alerts)
class DisasterAlertsIndex(AlgoliaIndex):
    # Remove datetime fields from direct fields tuple to avoid serialization issues
    fields = (
        'title',
        'description', 
        'location',
        'disaster_type',
        'population_affected',
        'latitude',
        'longitude',
        #'disaster_time',
    )
    
    settings = {
        'searchableAttributes': [
            'title',
            'description',
            'location',
            'disaster_type',
            'disaster_time_str',  # Use string version for search
        ],
        'attributesForFaceting': [
            'disaster_type',
            'location',
            'disaster_time_str',
            'population_affected',
        ],
        'customRanking': [
            'desc(disaster_time_timestamp)'
        ]
    }
    
    def get_queryset(self):
        return disaster_alerts.objects.all()
    
    def prepare_record(self, instance):
        """
        Override prepare_record to handle datetime serialization and coordinate extraction
        """
        # Start with basic fields (disaster_time is not included in fields to avoid serialization issues)
        record = {}
        for field in self.fields:
            value = getattr(instance, field, None)
            record[field] = value
        
        # Extract coordinates from location string if lat/lng fields are null
        if (not record.get('latitude') or not record.get('longitude')) and record.get('location'):
            import re
            # Pattern to match coordinates in format: (13.01, -90.98)
            coord_pattern = r'\((-?\d+\.?\d*),\s*(-?\d+\.?\d*)\)'
            match = re.search(coord_pattern, record['location'])
            if match:
                record['latitude'] = float(match.group(1))
                record['longitude'] = float(match.group(2))
        
        # Handle disaster_time (actual disaster occurrence time) with proper serialization
        if hasattr(instance, 'disaster_time') and instance.disaster_time:
            # Store as ISO string format for JSON serialization compatibility
            record['disaster_time'] = instance.disaster_time.isoformat()
            record['disaster_time_str'] = instance.disaster_time.strftime('%Y-%m-%d %H:%M:%S')  # Human readable
            record['disaster_time_timestamp'] = int(instance.disaster_time.timestamp())  # For sorting
        else:
            # If disaster_time is null, set appropriate defaults
            record['disaster_time'] = None
            record['disaster_time_str'] = 'Unknown'
            record['disaster_time_timestamp'] = 0
        
        # Set the primary key as objectID
        record['objectID'] = instance.pk
        record['id'] = instance.pk  # Also include id field as shown in your example
        
        return record