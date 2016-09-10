from django.db import models


class BusStation(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30)
    link = models.URLField(default='')
    address = models.CharField(max_length=255)
    sublocality = models.CharField(max_length=150, default='')
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class RouteStations(models.Model):
    DIRECTION_1 = 1
    DIRECTION_2 = 2

    direction = models.PositiveSmallIntegerField(
        choices=((DIRECTION_1, 'Ida'), (DIRECTION_2, 'Vuelta')),
    )
    position = models.PositiveIntegerField()
    route = models.ForeignKey('sitp_scraper.Route',
                              related_name='route_stations')
    bus_station = models.ForeignKey('sitp_scraper.BusStation')


class Route(models.Model):
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

    def __str__(self):
        return self.name
