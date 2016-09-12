from django.contrib import admin
from .models import BusStation, RouteStations, Route


@admin.register(BusStation)
class BusStationAdmin(admin.ModelAdmin):
    search_fields = ('code', 'name', 'address')
    list_display = ('name', 'code', 'address', 'longitude', 'latitude', 'created_at', 'updated_at')


@admin.register(RouteStations)
class RouteStationsAdmin(admin.ModelAdmin):
    list_display = ('direction', 'route', 'position', 'bus_station', 'created_at', 'updated_at')


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    search_fields = ('code', 'name')
    list_display = ('code', 'name', 'route_type', 'created_at', 'updated_at')
    ordering = ('code',)
