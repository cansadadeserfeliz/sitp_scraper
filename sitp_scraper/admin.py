from django.contrib import admin
from django.contrib.gis import admin as gis_admin
from django.utils.html import mark_safe

from .models import BusStation, RouteStations, Route


class RouteStationsInline(admin.TabularInline):
    model = RouteStations


@admin.register(BusStation)
class BusStationAdmin(gis_admin.OSMGeoAdmin):
    search_fields = ('code', 'name', 'address')
    list_display = (
        'name', 'code',
        'address', 'sublocality',
        'location', 'location_status',
        'created_at', 'updated_at',
        'source', 'sitp_url',
    )

    inlines = [
        RouteStationsInline,
    ]

    raw_id_fields = ('related_stations',)
    related_lookup_fields = {
        'm2m': ['related_stations'],
    }

    fieldsets = (
        (None, {
            'fields': ('name', 'code',)
        }),
        ('Address', {
            'fields': ('address', 'sublocality'),
        }),
        ('Map', {
            'fields': ('location', 'location_status',),
        }),
        ('SITP', {
            'fields': (('related_stations',), ('link',)),
        }),
    )

    openlayers_url = '//openlayers.org/api/2.13.1/OpenLayers.js'
    default_lon = -8248449
    default_lat = 520158
    default_zoom = 11

    def sitp_url(self, obj):
        if obj.link:
            return mark_safe('<a href="%s" target="_blank">SITP</a>' % obj.link)
        return ''


@admin.register(RouteStations)
class RouteStationsAdmin(admin.ModelAdmin):
    list_display = (
        'direction', 'route', 'position', 'bus_station',
        'created_at', 'updated_at'
    )

    raw_id_fields = ('bus_station', 'route',)
    related_lookup_fields = {
        'fk': ['bus_station', 'route'],
    }


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    search_fields = ('code', 'name')
    list_display = (
        'code_display', 'name', 'route_type', 'link',
        'created_at', 'updated_at'
    )

    def code_display(self, obj):
        if obj.route_type == Route.ROUTE_TYPE_URBAN:
            return mark_safe(
                '<span style="border-left: none; border-bottom: 5px solid #00608B;">%s</span>' % obj.code
            )
        elif obj.route_type == Route.ROUTE_TYPE_COMPLEMENTARY:
            return mark_safe(
                '<span style="border-left: none; border-bottom: 5px solid #D07400;">%s</span>' % obj.code
            )
        elif obj.route_type == Route.ROUTE_TYPE_SPECIAL:
            return mark_safe(
                '<span style="border-left: none; border-bottom: 5px solid #6C102D;">%s</span>' % obj.code
            )
        return obj.code
