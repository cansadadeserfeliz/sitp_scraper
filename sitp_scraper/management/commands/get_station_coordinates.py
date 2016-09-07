import requests

from django.core.management.base import BaseCommand
from sitp_scraper.models import BusStation


class Command(BaseCommand):
    help = 'Adds latitude and longitude to bus stations using ' \
           'Google Geocoder API'

    def handle(self, *args, **options):
        for bus_station in BusStation.objects.all():
            try:
                response = requests.get(
                    'http://maps.googleapis.com/maps/api/geocode/json?'
                    'address={}, Bogota%22&lang=es&components=country:CO'.format(
                        bus_station.address,
                    )
                )
                if response.status_code == 200:
                    response = response.json()
                    if response['status'] == 'OK':
                        for result in response['results']:
                            if 'bus_station' in result['types']:
                                continue
                            for address_component in result['address_components']:
                                if 'sublocality' in address_component['types']:
                                    bus_station.sublocality = address_component['long_name']
                                    break
                            bus_station.latitude = result['geometry']['location']['lat']
                            bus_station.longitude = result['geometry']['location']['lng']
                        bus_station.save()
            except Exception as e:
                print(bus_station.id, e.message)
            self.stdout.write(self.style.SUCCESS(
                'Bus stations coordinate were successfully updated'
            ))
