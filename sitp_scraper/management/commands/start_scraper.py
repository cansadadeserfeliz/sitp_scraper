import os

from scrapy.crawler import CrawlerProcess
from django.core.management.base import BaseCommand
from scrapy.utils.project import get_project_settings

from sitp_spider.spiders.routes_spider import SITPSpider

os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'sitp_spider.settings')


class Command(BaseCommand):
    help = 'Adds latitude and longitude to bus stations using ' \
           'Google Geocoder API'

    def handle(self, *args, **options):
        process = CrawlerProcess(settings=get_project_settings())

        process.crawl(SITPSpider)
        process.start()
