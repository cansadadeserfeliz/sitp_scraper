from ast import literal_eval

from django.db import models
from django.contrib.gis.db import models as geo_models


class BusStation(models.Model):
    LOCATION_VERIFIED = 1
    LOCATION_PENDING = 2
    LOCATION_WRONG = 3

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30)
    link = models.URLField(default='')
    address = models.CharField(max_length=255)
    sublocality = models.CharField(max_length=150, default='', blank=True)
    location_status = models.PositiveSmallIntegerField(
        choices=(
            (LOCATION_VERIFIED, 'Correcto'),
            (LOCATION_PENDING, 'Por validar'),
            (LOCATION_WRONG, 'Incorrecto'),
        ),
        default=LOCATION_PENDING,
    )
    location = geo_models.PointField(null=True)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=30, default='', blank=True)

    related_stations = models.ManyToManyField('self', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ('code__iexact', 'name__icontains',)

    class Meta:
        ordering = ['address']


class RouteStations(models.Model):
    DIRECTION_1 = 1
    DIRECTION_2 = 2

    direction = models.PositiveSmallIntegerField(
        choices=((DIRECTION_1, 'Ida'), (DIRECTION_2, 'Vuelta')),
    )
    position = models.PositiveIntegerField()
    route = models.ForeignKey('sitp_scraper.Route',
                              related_name='route_stations')
    bus_station = models.ForeignKey(
        'sitp_scraper.BusStation', related_name='route_stations')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['direction', 'position']


class Route(models.Model):
    ROUTE_TYPE_URBAN = 8
    ROUTE_TYPE_COMPLEMENTARY = 9
    ROUTE_TYPE_SPECIAL = 10
    ROUTE_TYPES = (
        (6, 'Troncal Sistema TransMilenio'),
        (7, 'Alimentadora'),
        (8, 'Urbana'),
        (9, 'Complementaria'),
        (10, 'Especial'),
    )

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30)
    route_type = models.PositiveSmallIntegerField(choices=ROUTE_TYPES)
    map_link = models.URLField(default='')
    schedule = models.CharField(max_length=500)
    link = models.URLField(default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def get_schedule_display(self):
        try:
            schedule = literal_eval(self.schedule)
            return ', '.join(schedule)
        except:
            return ''

    class Meta:
        ordering = ['code']
