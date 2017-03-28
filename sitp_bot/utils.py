import requests

from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string

from .models import SOURCE_FACEBOOK, SOURCE_TELEGRAM
from .models import BotUser, BotUserRequestStats, MessageStats
from sitp_scraper.models import Route, BusStation
from sitp_scraper import utils as sitp_utils

from python_bot_utils.telegram import send_markdown_message
from python_bot_utils.facebook import PostbackButton


def get_facebook_user_info(user_id):
    try:
        response = requests.get(
            'https://graph.facebook.com/v2.6/{user_id}'
            '?access_token={access_token}'.format(
                user_id=user_id,
                access_token=settings.FACEBOOK_PAGE_ACCESS_TOKEN,
            )
        )
        user_info = response.json()
    except:
        return {}
    return user_info


def save_bot_user(source, chat_user_id, user_info={}):
    bot_user, created = BotUser.objects.get_or_create(
        source=source,
        chat_user_id=chat_user_id,
    )
    if source == SOURCE_FACEBOOK:
        user_info = get_facebook_user_info(chat_user_id)

    # It can be Facebook user or Facebook page
    bot_user.first_name = \
        user_info.get('first_name', '') or user_info.get('name', '')
    bot_user.last_name = user_info.get('last_name', '')
    bot_user.username = user_info.get('username', '')
    bot_user.timezone = user_info.get('timezone', None)
    bot_user.locale = user_info.get('locale', '')

    bot_user.requests_count += 1
    bot_user.save()

    # Save user daily stats
    today = timezone.now().date()
    bot_user_request, created = BotUserRequestStats.objects.get_or_create(
        bot_user=bot_user,
        day=today,
    )
    bot_user_request.requests_count += 1
    bot_user_request.save()


def save_bot_message(source, message):
    bot_message, created = MessageStats.objects.get_or_create(
        phrase=message.lower().strip(),
        source=source,
    )
    bot_message.requests_count += 1
    bot_message.save()


def send_bus_info(bot_type, bot, chat_id, route=None):
    if route:
        if bot_type == SOURCE_TELEGRAM:
            message = render_to_string('bot/route_info.html', dict(route=route))
            send_markdown_message(bot, chat_id, message)
        elif bot_type == SOURCE_FACEBOOK:
            bot.sendMessage(chat_id, '''
            {code} {name} es una ruta {route_type}.
            '''.format(
                code=route.code,
                name=route.name,
                route_type=route.get_route_type_display(),
            ))
            bot.sendImage(chat_id, route.map_link)
    else:
        message = 'No conozco esa ruta :disappointed:'
        if bot_type == SOURCE_TELEGRAM:
            send_markdown_message(bot, chat_id, message)
        elif bot_type == SOURCE_FACEBOOK:
            bot.sendMessage(chat_id, message)


def send_bus_station_info(bot_type, bot, chat_id, bus_station=None):
    if not bus_station:
        message = 'No conozco esa parada :disappointed:'
        if bot_type == SOURCE_TELEGRAM:
            send_markdown_message(bot, chat_id, message)
        elif bot_type == SOURCE_FACEBOOK:
            bot.sendMessage(chat_id, message)
        return

    route_codes = [int(i) for i in set(bus_station.route_stations.values_list(
        'route__id', flat=True,
    ))]
    routes = Route.objects.filter(id__in=route_codes)
    message = render_to_string('bot/bus_station_info.html', dict(
        bus_station=bus_station,
        routes=routes,
    ))

    if bot_type == SOURCE_TELEGRAM:
        send_markdown_message(bot, chat_id, message)
    elif bot_type == SOURCE_FACEBOOK:
        buttons = []
        for route in routes:
            btn = PostbackButton(
                title='{}: {}'.format(route.code, route.name),
                payload='bus{}'.format(id),
            )
            buttons.append(btn)
        bot.sendButton(
            chat_id,
            ':bus: Parada {code} {name} / {address}'.format(
                code=bus_station.code,
                name=bus_station.name,
                address=bus_station.address,
            ),
            buttons
        )

    if bus_station.latitude and bus_station.longitude:
        if bot_type == SOURCE_TELEGRAM:
            bot.sendLocation(chat_id, bus_station.latitude, bus_station.longitude)
        elif bot_type == SOURCE_FACEBOOK:
            map_image_url = "https://api.mapbox.com/v4/mapbox.streets/pin-s+f44({long},{lat})/{long},{lat},15/300x200.png?access_token={access_token}".format(
                lat=float(bus_station.latitude),
                long=float(bus_station.longitude),
                access_token=settings.MAPBOX_ACCESS_TOKEN,
            )
            bot.sendImage(chat_id, map_image_url)


def send_nearest_bus_station(bot_type, bot, chat_id, location):
    bus_station = sitp_utils.get_closest_station(
        location['latitude'], location['longitude']
    )
    send_bus_station_info(bot_type, bot, chat_id, bus_station=bus_station)


def send_bus_or_station_info(bot_type, bot, chat_id, message_text):
    # Check for routes
    routes = Route.objects.filter(code__iexact=message_text).all()
    if routes:
        for route in routes:
            send_bus_info(bot_type, bot, chat_id, route)
        return True

    # Check for bus stations
    bus_station = BusStation.objects.filter(code__iexact=message_text).first()
    if bus_station:
        send_bus_station_info(bot_type, bot, chat_id, bus_station)
        return True

    return False
