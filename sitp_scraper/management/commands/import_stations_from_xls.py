import xlrd
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point

from sitp_scraper.models import BusStation


class Command(BaseCommand):
    help = 'Imports stations'

    def handle(self, *args, **options):
        book = xlrd.open_workbook(
            os.path.join(settings.BASE_DIR, 'data/20170113_SITP.XLSX'))
        sh = book.sheet_by_index(0)

        for rx in range(sh.nrows):
            if rx == 0:
                continue
            row = sh.row(rx)
            bus_station_code = row[0].value.strip()
            bs = BusStation.objects.filter(
                code__iexact=bus_station_code,
            ).first()
            if not bs:
                bs = BusStation()

            print(row)

            bs.code = bus_station_code.upper()
            bs.name = row[1].value.strip()
            bs.address = row[2].value.strip()
            bs.sublocality = row[3].value.strip()
            bs.location_status = BusStation.LOCATION_VERIFIED
            bs.location = Point(row[4].value, row[5].value)
            bs.source = 'movilidadbogota'
            bs.save()
