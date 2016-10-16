from django.http import JsonResponse
from django.views.generic import ListView, DetailView

from .models import Route, BusStation, RouteStations


def get_routes(request):
    features = []
    for bus_station in BusStation.objects.prefetch_related('route_stations').all():
        if bus_station.longitude and bus_station.latitude:
            routes = set(bus_station.route_stations.values_list(
                'route__code', flat=True,
            ))
            features.append({
                "type": "Feature",
                'properties': {
                    'title': '{}: {} ({})'.format(
                        bus_station.name,
                        bus_station.address,
                        ', '.join(routes)
                    ),
                    'marker-color': "#00608B",
                    'marker-size': 'small',
                    'marker-symbol': 'bus',
                },
                "geometry": {
                "type": "Point",
                "coordinates": [bus_station.longitude, bus_station.latitude]
                }
            })
    return JsonResponse({
      "type": "FeatureCollection",
      "features": features,
    })


def get_route(request, pk):
    features = []
    route = Route.objects.get(id=pk)
    for bs in route.route_stations.all():
        if bs.bus_station.longitude and bs.bus_station.latitude:
            features.append({
                "type": "Feature",
                "properties": {
                    "marker-color": "#00608B",
                    "marker-symbol": "bus",
                    "marker-size": "small",
                    "title": '{}: {}'.format(bs.bus_station.name, bs.bus_station.address)
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        bs.bus_station.longitude,
                        bs.bus_station.latitude,
                    ]
                }
            })
    bs_list = list(route.route_stations.filter(
        bus_station__longitude__isnull=False,
        bus_station__latitude__isnull=False,
    ))
    for bs1, bs2 in zip(bs_list[:-1], bs_list[1:]):
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [
                    [bs1.bus_station.longitude, bs1.bus_station.latitude],
                    [bs2.bus_station.longitude, bs2.bus_station.latitude]
                ]
            },
            'properties': {
                "stroke": "#ff8888",
                "stroke-opacity": 1,
                "stroke-width": 4,
            }
        })
    return JsonResponse({
        "type": "FeatureCollection",
        "features": features,
    })


class RouteListView(ListView):
    template_name = 'route_list.html'
    model = Route


class RouteDetailView(DetailView):
    template_name = 'route_detail.html'
    model = Route

    def get_context_data(self, **kwargs):
        context = super(RouteDetailView, self).get_context_data(**kwargs)
        context['route_1'] = self.object.route_stations.filter(
            direction=RouteStations.DIRECTION_1,
        ).all()
        context['route_2'] = self.object.route_stations.filter(
            direction=RouteStations.DIRECTION_2,
        ).all()
        return context
