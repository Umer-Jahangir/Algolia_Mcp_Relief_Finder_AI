import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from disasters.models import disaster_alerts
from algoliasearch_django.decorators import disable_auto_indexing


def get_child_text(item, name):
    for child in item:
        if child.tag.split('}')[-1] == name:
            return (child.text or '').strip()
    return None


class Command(BaseCommand):
    help = 'Fetch disaster alerts from GDACS and ReliefWeb RSS feeds (last 30 days).'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=1000, help='Max number of events to process (default: 1000)')

    def handle(self, *args, **options):
        with disable_auto_indexing():
            limit = options['limit']
            cutoff_date = (datetime.utcnow() - timedelta(days=30)).date()
            new_count = updated_count = 0

            # ---------------- GDACS RSS ----------------
            gdacs_url = 'https://www.gdacs.org/Xml/rssarchive.xml'
            self.stdout.write(self.style.SUCCESS('Fetching GDACS RSS...'))
            try:
                resp = requests.get(gdacs_url, timeout=30)
                resp.raise_for_status()
                root = ET.fromstring(resp.content)
                items = root.findall('.//item')[:limit]
                self.stdout.write(f'Found {len(items)} GDACS items.')
            except Exception as e:
                self.stderr.write(f'Error fetching GDACS RSS: {e}')
                items = []

            for item in items:
                pub = get_child_text(item, 'pubDate')
                try:
                    dt = datetime.strptime(pub, '%a, %d %b %Y %H:%M:%S %Z')
                except:
                    try:
                        dt = datetime.fromisoformat(pub.replace('Z', '+00:00'))
                    except:
                        continue
                if dt.date() < cutoff_date:
                    continue
                aware_dt = timezone.make_aware(dt) if timezone.is_naive(dt) else dt

                title = get_child_text(item, 'title') or ''
                description = get_child_text(item, 'description') or ''
                eventid = get_child_text(item, 'eventid') or get_child_text(item, 'link')
                eventtype = get_child_text(item, 'eventtype') or ''
                population = 0
                lat = lon = None

                if eventid and eventtype:
                    try:
                        detail_url = f'https://www.gdacs.org/gdacsapi/api/events/geteventdata?eventtype={eventtype}&eventid={eventid}&format=json'
                        dresp = requests.get(detail_url, timeout=20)
                        dresp.raise_for_status()
                        data = dresp.json().get('event', {})
                        population = int(data.get('populationExposure') or 0)
                        lat = float(data.get('latitude') or 0)
                        lon = float(data.get('longitude') or 0)
                        description = data.get('description') or description
                    except:
                        pass

                loc_str = f"{title} ({lat}, {lon})" if lat and lon else title
                obj = disaster_alerts.objects.filter(title=title, location=loc_str).first()
                if obj:
                    changed = False
                    if not obj.disaster_time:
                        obj.disaster_time = aware_dt; changed = True
                    if obj.population_affected == 0 and population > 0:
                        obj.population_affected = population; changed = True
                    if obj.latitude is None and lat:
                        obj.latitude = lat; changed = True
                    if obj.longitude is None and lon:
                        obj.longitude = lon; changed = True
                    if changed:
                        obj.disaster_type = eventtype or obj.disaster_type
                        obj.description = description or obj.description
                        obj.save()
                        updated_count += 1
                        self.stdout.write(f'Updated (GDACS): {title}')
                else:
                    disaster_alerts.objects.create(
                        title=title,
                        description=description,
                        location=loc_str,
                        disaster_type=eventtype,
                        population_affected=population,
                        disaster_time=aware_dt,
                        latitude=lat,
                        longitude=lon,
                        created_at=aware_dt
                    )
                    new_count += 1
                    self.stdout.write(f'Added (GDACS): {title}')

            # ---------------- ReliefWeb RSS ----------------
            relief_url = 'https://reliefweb.int/disasters/rss.xml'
            self.stdout.write(self.style.SUCCESS('Fetching ReliefWeb RSS...'))

            try:
                rresp = requests.get(relief_url, timeout=30)
                rresp.raise_for_status()
                rroot = ET.fromstring(rresp.content)
                ritems = rroot.findall('.//item')[:limit]
                self.stdout.write(f'Found {len(ritems)} ReliefWeb items.')
            except Exception as e:
                self.stderr.write(f'Error fetching ReliefWeb RSS: {e}')
                ritems = []

            for item in ritems:
                pub = get_child_text(item, 'pubDate')
                try:
                    dt = datetime.strptime(pub, '%a, %d %b %Y %H:%M:%S %Z')
                except:
                    try:
                        dt = datetime.fromisoformat(pub.replace('Z', '+00:00'))
                    except:
                        continue
                if dt.date() < cutoff_date:
                    continue
                aware_dt = timezone.make_aware(dt) if timezone.is_naive(dt) else dt

                title = get_child_text(item, 'title') or ''
                description = get_child_text(item, 'description') or ''
                link = get_child_text(item, 'link') or ''
                loc_str = title
                eventtype = 'ReliefWeb Alert'

                obj = disaster_alerts.objects.filter(title=title, location=loc_str).first()
                if obj:
                    if not obj.disaster_time:
                        obj.disaster_time = aware_dt
                        obj.save()
                        updated_count += 1
                        self.stdout.write(f'Updated (ReliefWeb): {title}')
                else:
                    disaster_alerts.objects.create(
                        title=title,
                        description=description,
                        location=loc_str,
                        disaster_type=eventtype,
                        population_affected=0,
                        disaster_time=aware_dt,
                        latitude=None,
                        longitude=None,
                        created_at=aware_dt
                    )
                    new_count += 1
                    self.stdout.write(f'Added (ReliefWeb): {title}')

            self.stdout.write(self.style.SUCCESS(
                f'Done. New: {new_count}, Updated: {updated_count} (since {cutoff_date})'
            ))
