from scrapy.crawler import CrawlerProcess
from django.core.management.base import BaseCommand

from sitp_spider.spiders.routes_spider import SITPSpider


class Command(BaseCommand):
    help = 'Adds latitude and longitude to bus stations using ' \
           'Google Geocoder API'

    def handle(self, *args, **options):
        process = CrawlerProcess()

        process.crawl(SITPSpider)
        process.start()
