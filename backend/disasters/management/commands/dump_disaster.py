from django.core.management.base import BaseCommand
from disasters.models import disaster_alerts
import json

class Command(BaseCommand):
    help = 'Print all disaster_alerts records as JSON using the to_dict() helper'

    def handle(self, *args, **options):
        qs = disaster_alerts.objects.order_by('-created_at')
        for d in qs:
            # use ensure_ascii=False for readable non-ASCII characters
            self.stdout.write(json.dumps(d.to_dict(), ensure_ascii=False))
