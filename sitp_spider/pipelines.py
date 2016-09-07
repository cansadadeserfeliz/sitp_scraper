# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sitp_scraper.models import Route


class SitpSpiderPipeline(object):
    def process_item(self, item, spider):
        return item

    def process_item(self, item, spider):
        route = Route.objects.filter(code=item['code']).first()
        if route:
            Route.objects.filter(code=item['code']).update(**item)
        else:
            item.save()
        return item
