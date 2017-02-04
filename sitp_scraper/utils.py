from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from .models import BusStation


def get_closest_station(latitude, longitude):
    distance = 2000  # meters
    ref_location = Point(longitude, latitude)

    return BusStation.objects.filter(
        location__distance_lte=(ref_location, D(m=distance))
    ).annotate(
        distance=Distance('location', ref_location)
    ).order_by('distance').first()
