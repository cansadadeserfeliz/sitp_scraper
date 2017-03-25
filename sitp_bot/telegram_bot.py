from django.template.loader import render_to_string

from sitp_scraper.models import Route, BusStation

from sitp_scraper import utils as sitp_utils
from python_bot_utils.telegram import send_markdown_message


def send_help_message(bot, chat_id, first_name=''):
    send_markdown_message(bot, chat_id, render_to_string('bot/help.html', dict(
        first_name=first_name,
    )))


def send_bus_or_station_info(bot, chat_id, message_text):
    # Check for routes
    routes = Route.objects.filter(code__iexact=message_text).all()
    if routes:
        for route in routes:
            send_bus_info(bot, chat_id, route)
        return True

    # Check for bus stations
    bus_station = BusStation.objects.filter(code__iexact=message_text).first()
    if bus_station:
        send_bus_station_info(bot, chat_id, bus_station)
        return True

    return False


def send_bus_info(bot, chat_id, route=None):
    if route:
        message = render_to_string('bot/route_info.html', dict(route=route))
    else:
        message = 'No conozco esa ruta :disappointed:'
    send_markdown_message(bot, chat_id, message)


def send_bus_station_info(bot, chat_id, bus_station=None):
    if not bus_station:
        send_markdown_message(bot, chat_id, 'No conozco esa parada :disappointed:')
        return

    route_codes = [int(i) for i in set(bus_station.route_stations.values_list(
        'route__id', flat=True,
    ))]
    routes = Route.objects.filter(id__in=route_codes)
    message = render_to_string('bot/bus_station_info.html', dict(
        bus_station=bus_station,
        routes=routes,
    ))
    send_markdown_message(bot, chat_id, message)
    if bus_station.latitude and bus_station.longitude:
        bot.sendLocation(chat_id, bus_station.latitude, bus_station.longitude)


def send_nearest_bus_station(bot, chat_id, location):
    bus_station = sitp_utils.get_closest_station(
        location['latitude'], location['longitude']
    )
    send_bus_station_info(bot, chat_id, bus_station=bus_station)
