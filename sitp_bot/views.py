import json
import logging
import telepot

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

    def display_bus_info(self, route_code):
        route = Route.objects.filter(code__iexact=route_code).first()
        if not route:
            return 'No conozco esa ruta {}'.format(EMOJI_CODES['disappointed'])
        return render_to_string('bot/bus_info.html', dict(
            route=route,
            #route_1=route.route_stations.filter(
            #    direction=RouteStations.DIRECTION_1,
            #).all(),
            #route_2=route.route_stations.filter(
            #    direction=RouteStations.DIRECTION_2,
            #).all(),
            EMOJI_CODES=EMOJI_CODES,
        ))

    def display_bus_station_info(self, bus_station_code):
        bus_station = BusStation.objects.filter(
            code__iexact=bus_station_code,
        ).first()
        if not bus_station:
            return 'No conozco esa parada {}'.format(EMOJI_CODES['disappointed'])
        route_codes = [int(i) for i in set(bus_station.route_stations.values_list(
            'route__id', flat=True,
        ))]
        routes = Route.objects.filter(id__in=route_codes)
        return render_to_string('bot/bus_station_info.html', dict(
            bus_station=bus_station,
            routes=routes,
            EMOJI_CODES=EMOJI_CODES,
        ))

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
        else:
            chat_id = payload['message']['chat']['id']
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
                    TelegramBot.sendMessage(
                        chat_id,
                        self.display_bus_info(words[1]),
                        parse_mode='Markdown')
            elif cmd == '/parada':
                if len(words) != 2:
                    TelegramBot.sendMessage(
                        chat_id,
                        'Tienes que escribir el número de la parada. '
                        'Por ejemplo, /parada 216B00')
                else:
                    TelegramBot.sendMessage(
                        chat_id,
                        self.display_bus_station_info(words[1]),
                        parse_mode='Markdown')
            else:
                TelegramBot.sendMessage(
                    chat_id,
                    'No te entiendo {} '
                    'Escribe /help para saber cómo hablar conmigo'.format(
                        EMOJI_CODES['confused_face']
                    )
                )

        return JsonResponse({}, status=200)


