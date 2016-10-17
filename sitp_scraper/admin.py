from django.contrib import admin
from django.utils.html import mark_safe

from .models import BusStation, RouteStations, Route


@admin.register(BusStation)
class BusStationAdmin(admin.ModelAdmin):
    search_fields = ('code', 'name', 'address')
    list_display = (
        'name', 'code',
        'address', 'sublocality',
        'longitude', 'latitude',
        'created_at', 'updated_at',
        'sitp_url',
    )

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
            'description': '<div id="map"></div>',
            'fields': ('longitude', 'latitude'),
        }),
        ('SITP', {
            'fields': (('related_stations',), ('link',)),
        }),
    )

    def sitp_url(self, obj):
        if obj.link:
            return mark_safe('<a href="%s" target="_blank">SITP</a>' % obj.link)
        return ''

    class Media:
        css = {
            "all": (
                "https://api.mapbox.com/mapbox.js/v2.4.0/mapbox.css",
                "css/admin_map.css",
            )
        }
        js = (
            "https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js",
            "https://api.mapbox.com/mapbox.js/v2.4.0/mapbox.js",
            "js/admin_map.js",
        )

@admin.register(RouteStations)
class RouteStationsAdmin(admin.ModelAdmin):
    list_display = (
        'direction', 'route', 'position', 'bus_station',
        'created_at', 'updated_at'
    )


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
