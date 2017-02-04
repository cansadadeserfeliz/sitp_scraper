import json
import logging
import telepot
from geopy.distance import great_circle

from django.views.generic import View
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.template.loader import render_to_string

from sitp_bot.facebook_bot import received_message as facebook_received_message
from sitp_scraper.models import Route, RouteStations, BusStation
from sitp_bot.utils import EMOJI_CODES


TelegramBot = telepot.Bot(settings.TELEGRAM_TOKEN)
telegram_logger = logging.getLogger('telegram.bot')
facebook_logger = logging.getLogger('facebook.bot')


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
            telegram_logger.info(
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


class FacebookCommandReceiveView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(FacebookCommandReceiveView, self).dispatch(request, *args, **kwargs)

    def get(self, request, bot_keyword):
        if request.GET.get('hub.mode') == 'subscribe' and request.GET.get('hub.verify_token') == settings.FACEBOOK_VERIFY_TOKEN:
            return HttpResponse(request.GET.get('hub.challenge'))
        else:
            return HttpResponseForbidden()

    def post(self, request, bot_keyword):
        if bot_keyword != settings.FACEBOOK_VERIFY_TOKEN:
            return HttpResponseForbidden('Invalid token')

        data = json.loads(request.body.decode('utf-8'))
        facebook_logger.info('FB bot', extra={'data': data})

        # Make sure this is a page subscription
        if data['object'] == 'page':
            # Iterate over each entry - there may be multiple if batched
            for entry in data['entry']:
                # Iterate over each messaging event
                for event in entry['messaging']:
                    if event.get('message'):
                        facebook_received_message(event)
                    elif event.get('delivery'):
                        pass
                        #logger.info('FB. Message delivered: {}'.format(event))
                    elif event.get('read'):
                        pass
                        #logger.info('FB. Message read: {}'.format(event))
                    elif event.get('postback'):
                        facebook_logger.info('FB. Message is postback: {}'.format(event))
                    elif event.get('optin'):
                        facebook_logger.info('FB. Message is optin: {}'.format(event))
                    elif event.get('referral'):
                        facebook_logger.info('FB. Message is referral: {}'.format(event))
                    elif event.get('account_linking'):
                        facebook_logger.info('FB. Message is account linking: {}'.format(event))
                    else:
                        facebook_logger.info('Webhook received unknown event: {}'.format(event))

        # Assume all went well.
        # You must send back a 200, within 20 seconds, to let us know
        # you've successfully received the callback. Otherwise, the request
        # will time out and we will keep trying to resend.
        return HttpResponse()
