# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BusStationItem(scrapy.Item):
    name = scrapy.Field()
    code = scrapy.Field()
    link = scrapy.Field()
    address = scrapy.Field()
    sublocality = scrapy.Field()
    longitude = scrapy.Field()
    latitude = scrapy.Field()


class RouteItem(scrapy.Item):
    code = scrapy.Field()
    name = scrapy.Field()
    bus_type = scrapy.Field()
    map_link = scrapy.Field()
    schedule = scrapy.Field()
    link = scrapy.Field()
    route_1 = scrapy.Field()
    route_2 = scrapy.Field()
