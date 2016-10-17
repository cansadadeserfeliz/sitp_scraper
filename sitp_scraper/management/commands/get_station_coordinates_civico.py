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
            code__isnull=False,
        ).all():
            print(bus_station.name, bus_station.address, bus_station.code)
            try:
                url = 'https://www.civico.com/bogota/busqueda/' \
                      'autocomplete_entity?search={}'.format(
                          bus_station.code,
                      )
                print('\t', url)
                response = requests.get(url)
                print('\t', response.status_code)
                if response.status_code == 200:
                    response = response.json()
                    if response.get('entities'):
                        for entity in response['entities']:
                            if 'SITP' not in entity['name']:
                                continue
                            address = entity['address'][0]
                            print('\t', address)
                            bus_station.longitude = address['coordinates'][0]
                            bus_station.latitude = address['coordinates'][1]
                            print('\t', bus_station.longitude, bus_station.latitude)
                            bus_station.source = 'civico'
                            bus_station.save()
                            self.stdout.write(self.style.SUCCESS(
                                '\t Bus stations coordinate were successfully updated'
                            ))
                        continue
            except Exception as e:
                print(bus_station.id, e)
            print('...Next station')
