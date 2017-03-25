import json
import logging
import telepot
import re

from django.views.generic import View
from django.http import (
    JsonResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse,
)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import SOURCE_TELEGRAM
from .utils import save_bot_message, save_bot_user
from .telegram_bot import (
    send_help_message, send_bus_or_station_info, send_nearest_bus_station,
    send_bus_info,
)
from .facebook_bot import received_message as facebook_received_message
from sitp_scraper.models import Route
from python_bot_utils.telegram import send_markdown_message


TelegramBot = telepot.Bot(settings.TELEGRAM_TOKEN)
telegram_logger = logging.getLogger('telegram.bot')
facebook_logger = logging.getLogger('facebook.bot')


class TelegramCommandReceiveView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TelegramCommandReceiveView, self).dispatch(request, *args, **kwargs)

    def post(self, request, bot_token):
        if bot_token != settings.TELEGRAM_TOKEN:
            return HttpResponseForbidden('Invalid token')

        try:
            raw = request.body.decode('utf-8')
            payload = json.loads(raw)
            telegram_logger.info('Telegram Bot request', extra={'data': payload})
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')

        first_name = ''

        # Save bot user
        if payload['message'].get('from'):
            first_name = payload['message']['from']['first_name']
            user_id = payload['message']['from'].get('id', '')
            save_bot_user(SOURCE_TELEGRAM, user_id, payload['message']['from'])

        response = JsonResponse({}, status=200)
        chat_id = payload['message']['chat']['id']

        # If we got user location
        location = payload['message'].get('location')
        if location:
            send_nearest_bus_station(TelegramBot, chat_id, location)
            return response

        message_text = payload['message'].get('text')

        if not message_text:
            return response

        save_bot_message(SOURCE_TELEGRAM, message_text)
        message_text = message_text.lower().strip()

        if message_text in ['/start', '/help', '/info']:
            send_help_message(TelegramBot, chat_id, first_name)
            return response

        bus_match = re.fullmatch(r'/bus(\d+)', message_text)
        if bus_match:
            route = Route.objects.filter(id=bus_match.group(1)).first()
            send_bus_info(TelegramBot, chat_id, route)
            return response

        # Try to get bus station or route
        if not send_bus_or_station_info(TelegramBot, chat_id, message_text):
            send_markdown_message(
                TelegramBot,
                chat_id,
                'Tienes que escribir el número de bus o de la parada. \n'
                'Por ejemplo, *18-2* o *033A06* '
                '[foto](http://www.sitp.gov.co/modulos/Rutas/img/ParaderosPuntoParada.png)',
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
