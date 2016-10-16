import requests

from scrapy.selector import Selector

from django.core.management.base import BaseCommand
from sitp_scraper.models import BusStation


class Command(BaseCommand):
    help = 'Finds composed stations'

    def handle(self, *args, **options):
        for bus_station in BusStation.objects.all():
            print(bus_station.name, bus_station.address, bus_station.link)
            try:
                response = requests.get(bus_station.link)
                print('\t', response.status_code)
                if response.status_code == 200:
                    response_text = response.text
                    is_combined_station = 'de un paradero m' in response_text
                    print(is_combined_station)
                    res = Selector(text=response_text).css(
                        '#zonaBloqueContent h3::text').extract_first()
                    if not res:
                        continue
                    code, name = res.split('-')
                    code = code.replace('Paradero', '').strip()
                    print(code)
                    if not bus_station.code:
                        bus_station.code = code
                        bus_station.save()

                    for other_station in Selector(text=response_text).css(
                        '.moduloParaderoMultiple a'):
                        other_station_code = other_station.css(
                            '.codigoParadero::text').extract_first()
                        station = BusStation.objects.filter(
                            code=other_station_code).first()
                        if station:
                            if (
                                station.latitude and station.longitude
                                and not bus_station.latitude
                            ):
                                bus_station.latitude = station.latitude
                                bus_station.longitude = station.longitude
                                bus_station.save()
                                continue
                            if (
                                bus_station.latitude and bus_station.longitude
                                and not station.latitude
                            ):
                                station.latitude = bus_station.latitude
                                station.longitude = bus_station.longitude
                                station.save()
                                continue
                    if not res:
                        continue
            except Exception as e:
                print(bus_station.id, e)
            print('...Next station')
