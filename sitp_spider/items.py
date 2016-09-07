# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem

from sitp_scraper.models import BusStation, Route


class BusStationItem(scrapy.Item):
    django_model = BusStation


class RouteItem(scrapy.Item):
    django_model = Route
