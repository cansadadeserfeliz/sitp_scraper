import json
import logging
import telepot
from geopy.distance import great_circle

from django.views.generic import View
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.template.loader import render_to_string

from sitp_scraper.models import Route, RouteStations, BusStation
from sitp_bot.utils import EMOJI_CODES


TelegramBot = telepot.Bot(settings.TELEGRAM_TOKEN)
logger = logging.getLogger('telegram.bot')


class CommandReceiveView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)

    def display_help(self, first_name):
        return render_to_string('bot/help.html', dict(
            first_name=first_name,
            EMOJI_CODES=EMOJI_CODES,
        ))

    def send_bus_info(self, chat_id, route_code):
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
        TelegramBot.sendMessage(chat_id, message, parse_mode='Markdown')

    def send_bus_station_info(self, chat_id, bus_station_code):
        bus_station = BusStation.objects.filter(
            code__iexact=bus_station_code,
        ).first()
        if not bus_station:
            message = 'No conozco esa parada {}'.format(EMOJI_CODES['disappointed'])
            TelegramBot.sendMessage(chat_id, message, parse_mode='Markdown')
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
        TelegramBot.sendMessage(chat_id, message, parse_mode='Markdown')
        if bus_station.latitude and bus_station.longitude:
            TelegramBot.sendLocation(chat_id, bus_station.latitude, bus_station.longitude)

    def send_nearest_bus_station(self, chat_id, location):
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
        self.send_bus_station_info(chat_id, BusStation.objects.filter(
            latitude=nearest[0],
            longitude=nearest[1],
        ).first().code)

    def post(self, request, bot_token):
        if bot_token != settings.TELEGRAM_TOKEN:
            return HttpResponseForbidden('Invalid token')

        raw = request.body.decode('utf-8')

        try:
            payload = json.loads(raw)
            first_name = payload['message']['from'].get('first_name', '')
            logger.info(
                'Bot request from {}'.format(first_name),
                extra={'data': payload}
            )
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')

        response = JsonResponse({}, status=200)
        chat_id = payload['message']['chat']['id']

        location = payload['message'].get('location')
        if location:
            self.send_nearest_bus_station(chat_id, location)
            return response

        text = payload['message'].get('text')
        words = text.split()
        cmd = words[0].lower()

        if cmd == '/start':
            TelegramBot.sendMessage(
                chat_id,
                self.display_help(first_name),
                parse_mode='Markdown')
        elif cmd == '/help':
            TelegramBot.sendMessage(
                chat_id,
                self.display_help(first_name),
                parse_mode='Markdown')
        elif cmd == '/bus':
            if len(words) != 2:
                TelegramBot.sendMessage(
                    chat_id,
                    'Tienes que escribir el número de la ruta. '
                    'Por ejemplo, /bus 18-2')
            else:
                self.send_bus_info(chat_id, words[1]),
                return response
        elif cmd == '/parada':
            if len(words) != 2:
                TelegramBot.sendMessage(
                    chat_id,
                    'Tienes que escribir el número de la parada. '
                    'Por ejemplo, /parada 216B00')
            else:
                self.send_bus_station_info(chat_id, words[1])
                return response
        else:
            TelegramBot.sendMessage(
                chat_id,
                'No te entiendo {} '
                'Escribe /help para saber cómo hablar conmigo'.format(
                    EMOJI_CODES['confused_face']
                )
            )

        return response


