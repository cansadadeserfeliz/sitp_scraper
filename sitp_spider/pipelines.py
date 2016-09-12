# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from django.utils import timezone

from sitp_scraper.models import Route, BusStation, RouteStations


class SitpSpiderPipeline(object):

    @staticmethod
    def get_station(station_item):
        station = BusStation.objects.filter(address=station_item['address']).first()

        if station:
            # We'll get latitude and longitude from Google Maps
            del station_item['latitude']
            del station_item['longitude']

            BusStation.objects.filter(
                address=station_item['address'],
            ).update(updated_at=timezone.now(), **station_item)
        else:
            station = station_item.save()
        return station

    def process_item(self, item, spider):
        route = Route.objects.filter(code=item['code']).first()

        route_1 = item['route_1']
        route_2 = item['route_2']

        del item['route_1']
        del item['route_2']

        if route:
            Route.objects.filter(
                code=item['code'],
            ).update(updated_at=timezone.now(), **item)
        else:
            item.save()

        RouteStations.objects.filter(route=route).delete()

        for i, station_item in enumerate(route_1, start=1):
            RouteStations.objects.create(
                direction=RouteStations.DIRECTION_1,
                position=i,
                bus_station=self.get_station(station_item),
                route=route,
            )

        for i, station_item in enumerate(route_2, start=1):
            RouteStations.objects.create(
                direction=RouteStations.DIRECTION_2,
                position=i,
                bus_station_id=self.get_station(station_item).id,
                route=route,
            )

        return item
