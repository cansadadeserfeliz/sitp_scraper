from geopy.distance import great_circle

from django.template.loader import render_to_string

from sitp_scraper.models import Route, RouteStations, BusStation

from sitp_bot.utils import EMOJI_CODES


def display_help(bot, first_name):
    return render_to_string('bot/help.html', dict(
        first_name=first_name,
        EMOJI_CODES=EMOJI_CODES,
    ))


def send_bus_info(bot, chat_id, route_code):
    route = Route.objects.filter(code__iexact=route_code).first()
    if not route:
        message = \
            'No conozco esa ruta {}'.format(EMOJI_CODES['disappointed'])
    else:
        message = render_to_string('bot/bus_info.html', dict(
            route=route,
            #route_1=route.route_stations.filter(
            #    direction=RouteStations.DIRECTION_1,
            #).all(),
            #route_2=route.route_stations.filter(
            #    direction=RouteStations.DIRECTION_2,
            #).all(),
            EMOJI_CODES=EMOJI_CODES,
        ))
    bot.sendMessage(chat_id, message, parse_mode='Markdown')


def send_bus_station_info(bot, chat_id, bus_station_code):
    bus_station = BusStation.objects.filter(
        code__iexact=bus_station_code,
    ).first()
    if not bus_station:
        message = 'No conozco esa parada {}'.format(EMOJI_CODES['disappointed'])
        bot.sendMessage(chat_id, message, parse_mode='Markdown')
        return
    route_codes = [int(i) for i in set(bus_station.route_stations.values_list(
        'route__id', flat=True,
    ))]
    routes = Route.objects.filter(id__in=route_codes)
    message = render_to_string('bot/bus_station_info.html', dict(
        bus_station=bus_station,
        routes=routes,
        EMOJI_CODES=EMOJI_CODES,
    ))
    bot.sendMessage(chat_id, message, parse_mode='Markdown')
    if bus_station.latitude and bus_station.longitude:
        bot.sendLocation(chat_id, bus_station.latitude, bus_station.longitude)


def send_nearest_bus_station(bot, chat_id, location):
    min_latitude = 0.01
    min_longitude = 0.01
    bus_stations = {
        bs.code: (bs.latitude, bs.longitude)
        for bs in BusStation.objects.filter(
            latitude__gte=location['latitude'] - min_latitude,
            latitude__lte=location['latitude'] + min_latitude,
            longitude__gte=location['longitude'] - min_longitude,
            longitude__lte=location['longitude'] + min_longitude,
        )
    }

    def distance(x, y):
        return great_circle(x, y).miles

    nearest = min(
        bus_stations.values(),
        key=lambda x: distance(
            x,
            (location['latitude'], location['longitude'])
        )
    )
    send_bus_station_info(bot, chat_id, BusStation.objects.filter(
        latitude=nearest[0],
        longitude=nearest[1],
    ).first().code)
