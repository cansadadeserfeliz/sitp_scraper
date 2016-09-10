from django.contrib import admin
from .models import BusStation, RouteStations, Route


@admin.register(BusStation)
class BusStationAdmin(admin.ModelAdmin):
    pass


@admin.register(RouteStations)
class RouteStationsAdmin(admin.ModelAdmin):
    pass


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    pass
