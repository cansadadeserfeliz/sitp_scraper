import json
import logging
import telepot

from django.views.generic import View
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from sitp_scraper.models import Route


TelegramBot = telepot.Bot(settings.TELEGRAM_TOKEN)
logger = logging.getLogger('telegram.bot')


class CommandReceiveView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)

    def display_help(self):
        return 'Hi'

    def display_bus_info(self):
        route = Route.objects.first()
        return route.code

    def post(self, request, bot_token):
        if bot_token != settings.TELEGRAM_TOKEN:
            return HttpResponseForbidden('Invalid token')

        commands = {
            '/start': self.display_help,
            'help': self.display_help,
            '/bus': self.display_bus_info,
        }

        raw = request.body.decode('utf-8')
        logger.info(raw)

        try:
            payload = json.loads(raw)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            chat_id = payload['message']['chat']['id']
            text = payload['message'].get('text')  # command

            func = commands.get(text.split()[0].lower())
            if func:
                TelegramBot.sendMessage(chat_id, func(), parse_mode='Markdown')
            else:
                TelegramBot.sendMessage(chat_id, 'I do not understand you, Sir!')

        return JsonResponse({}, status=200)


