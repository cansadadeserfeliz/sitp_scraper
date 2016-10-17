import requests

from django.core.management.base import BaseCommand
from sitp_scraper.models import BusStation


class Command(BaseCommand):
    help = 'Adds latitude and longitude to bus stations using ' \
           'Google Geocoder API'

    def handle(self, *args, **options):
        for bus_station in BusStation.objects.filter(
            latitude__isnull=True,
            longitude__isnull=True,
        ).all():
            print(bus_station.name, bus_station.address)
            try:
                url = 'http://maps.googleapis.com/maps/api/geocode/json?' \
                      'address={}, Bogota%22&lang=es&components=country:CO'.format(
                          bus_station.address,
                      )
                print('\t', url)
                response = requests.get(url)
                print('\t', response.status_code)
                if response.status_code == 200:
                    response = response.json()
                    print('\t', response['status'])
                    if response['status'] == 'OK':
                        for result in response['results']:
                            print('\t is bus station', 'bus_station' in result['types'])
                            if 'bus_station' not in result['types']:
                                continue
                            for address_component in result['address_components']:
                                if 'sublocality' in address_component['types']:
                                    bus_station.sublocality = address_component['long_name']
                            print('\t', result['geometry']['location'])

                            bus_station.latitude = result['geometry']['location']['lat']
                            bus_station.longitude = result['geometry']['location']['lng']
                            bus_station.source = 'google'
                        print('\t', (bus_station.latitude, bus_station.longitude))
                        bus_station.save()
                        self.stdout.write(self.style.SUCCESS(
                            '\t Bus stations coordinate were successfully updated'
                        ))
                        continue
            except Exception as e:
                print(bus_station.id, e)
            print('...Next station')
