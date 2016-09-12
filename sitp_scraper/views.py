from django.http import JsonResponse
from django.views.generic import ListView, DetailView

from .models import Route, BusStation, RouteStations


def get_routes(request):
    features = []
    for bus_station in BusStation.objects.all():
        if bus_station.longitude and bus_station.latitude:
            features.append({
              "type": "Feature",
              "properties": {
                "marker-color": "#00608B",
                "marker-symbol": "bus",
                "marker-size": "small",
                "title": '{}: {}'.format(bus_station.name, bus_station.address)
              },
              "geometry": {
                "type": "Point",
                "coordinates": [
                  bus_station.longitude,
                  bus_station.latitude,
                ]
              }
            })

    route = Route.objects.get(code='544B')
    bs_list = list(route.route_stations.filter(
        direction=RouteStations.DIRECTION_1,
    ).all())
    prev_bs = bs_list[0].bus_station
    for bs in bs_list:
        if not (prev_bs.longitude and prev_bs.latitude):
            prev_bs = bs.bus_station
            continue
        if bs.bus_station.longitude and bs.bus_station.latitude:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [prev_bs.longitude,
                         prev_bs.latitude],
                        [bs.bus_station.longitude,
                         bs.bus_station.latitude],
                    ]
                },
                'properties': {
                    "stroke": "#ff8888",
                    "stroke-opacity": 1,
                    "stroke-width": 4,
                }
            })
        prev_bs = bs.bus_station

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
