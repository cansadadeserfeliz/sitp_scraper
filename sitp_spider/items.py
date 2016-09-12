# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy_djangoitem import DjangoItem

from sitp_scraper.models import BusStation, Route


class BusStationItem(DjangoItem):
    django_model = BusStation


class RouteItem(DjangoItem):
    django_model = Route
    route_1 = scrapy.Field()
    route_2 = scrapy.Field()
