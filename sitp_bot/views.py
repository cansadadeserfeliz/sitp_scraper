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
from .utils import EMOJI_CODES, save_bot_message, save_bot_user
from .telegram_bot import (
    display_help, send_bus_info, send_nearest_bus_station,
    send_bus_station_info,
)
from .facebook_bot import received_message as facebook_received_message


TelegramBot = telepot.Bot(settings.TELEGRAM_TOKEN)
telegram_logger = logging.getLogger('telegram.bot')
facebook_logger = logging.getLogger('facebook.bot')


class CommandReceiveView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)

    def post(self, request, bot_token):
        if bot_token != settings.TELEGRAM_TOKEN:
            return HttpResponseForbidden('Invalid token')

        raw = request.body.decode('utf-8')

        try:
            payload = json.loads(raw)
            first_name = payload['message']['from'].get('first_name', '')
            username = payload['message']['from'].get('username', '')
            user_id = payload['message']['from'].get('id', '')
            telegram_logger.info(
                'Bot request from {}'.format(username),
                extra={'data': payload}
            )
            save_bot_user(SOURCE_TELEGRAM, user_id, payload['message']['from'])
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')

        response = JsonResponse({}, status=200)
        chat_id = payload['message']['chat']['id']

        location = payload['message'].get('location')
        if location:
            send_nearest_bus_station(TelegramBot, chat_id, location)
            return response

        text = payload['message'].get('text')

        bus_match = re.fullmatch(r'/bus(\d+)', text)
        if bus_match:
            send_bus_info(TelegramBot, chat_id, bus_id=bus_match.group(1))
            return response

        cmd = ''
        if text:
            save_bot_message(SOURCE_TELEGRAM, text)
            words = text.split()
            cmd = words[0].lower()

        if cmd == '/start':
            TelegramBot.sendMessage(
                chat_id,
                display_help(TelegramBot, first_name),
                parse_mode='Markdown')
        elif cmd == '/help':
            TelegramBot.sendMessage(
                chat_id,
                display_help(TelegramBot, first_name),
                parse_mode='Markdown')
        elif cmd == '/bus':
            if len(words) != 2:
                TelegramBot.sendMessage(
                    chat_id,
                    'Tienes que escribir el número de la ruta. '
                    'Por ejemplo, /bus 18-2')
            else:
                send_bus_info(TelegramBot, chat_id, words[1]),
                return response
        elif cmd == '/parada':
            if len(words) != 2:
                TelegramBot.sendMessage(
                    chat_id,
                    'Tienes que escribir el número de la parada. \n'
                    'Por ejemplo, /parada 216B00 \n'
                    '[Foto](http://www.sitp.gov.co/modulos/Rutas/img/ParaderosPuntoParada.png)',
                    parse_mode='Markdown',
                )
            else:
                send_bus_station_info(TelegramBot, chat_id, words[1])
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
