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
    list_display = ('code_display', 'name', 'route_type', 'created_at', 'updated_at')
    ordering = ('code',)

    def code_display(self, obj):
        if obj.route_type == Route.ROUTE_TYPE_URBAN:
            return '<span style="border-left: none; border-bottom: 5px solid #00608B;">%s</span>' % obj.code
        elif obj.route_type == Route.ROUTE_TYPE_COMPLEMENTARY:
            return '<span style="border-left: none; border-bottom: 5px solid #D07400;">%s</span>' % obj.code
        return obj.code
    code_display.allow_tags = True
