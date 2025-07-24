# relief_shelter/management/commands/dump_relief.py

from django.core.management.base import BaseCommand
from relief_shelter.models import Relief_Shelter
import json

class Command(BaseCommand):
    help = 'Dump all relief shelter data to console (for review/debug)'

    def handle(self, *args, **options):
        shelters = Relief_Shelter.objects.all()
        for shelter in shelters:
            self.stdout.write(json.dumps({
                "id": shelter.id,
                "name": shelter.name,
                "address": shelter.address,
                "phone_number": shelter.phone_number,
                "has_bed": shelter.has_bed,
                "has_food": shelter.has_food,
                "has_water": shelter.has_water,
                "has_medical": shelter.has_medical,
                "is_24_7": shelter.is_24_7,
                "is_open": shelter.is_open,
                "total_spaces": shelter.total_spaces,
                "available_spaces": shelter.available_spaces,
                "latitude": shelter.latitude,
                "longitude": shelter.longitude,
            }, indent=4))
