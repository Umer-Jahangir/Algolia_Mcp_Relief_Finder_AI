# relief_shelter/index.py

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register
from .models import Relief_Shelter

@register(Relief_Shelter)
class ReliefShelterIndex(AlgoliaIndex):
    fields = (
        'name',
        'address',
        'phone_number',
        'has_bed',
        'has_food',
        'has_water',
        'has_medical',
        'is_24_7',
        'is_open',
        'total_spaces',
        'available_spaces',
        'latitude',
        'longitude',
    )

    settings = {
        'searchableAttributes': [
            'name',
            'address',
            'phone_number',
        ],
        'attributesForFaceting': [
            'has_bed',
            'has_food',
            'has_water',
            'has_medical',
            'is_open',
            'is_24_7',
        ],
        'customRanking': [
            'desc(available_spaces)',
            'asc(total_spaces)',
        ]
    }

    def get_queryset(self):
        return Relief_Shelter.objects.all()

    def prepare_record(self, instance):
        record = {}
        for field in self.fields:
            value = getattr(instance, field, None)
            record[field] = value

        # Fallback coordinate parsing (if lat/lng missing but present in address string)
        if (not record.get('latitude') or not record.get('longitude')) and record.get('address'):
            import re
            coord_pattern = r'\((-?\d+\.?\d*),\s*(-?\d+\.?\d*)\)'
            match = re.search(coord_pattern, record['address'])
            if match:
                record['latitude'] = float(match.group(1))
                record['longitude'] = float(match.group(2))

        # Add objectID and id for Algolia
        record['objectID'] = instance.pk
        record['id'] = instance.pk

        return record
