import logging
from django.conf import settings

from .models import SOURCE_FACEBOOK
from .utils import save_bot_user, save_bot_message, send_bus_or_station_info
from sitp_scraper import utils as sitp_utils
from python_bot_utils.facebook import MessengerBot, QuickReply

logger = logging.getLogger('facebook.bot')


def received_message(event):
    bot = MessengerBot(settings.FACEBOOK_PAGE_ACCESS_TOKEN)

    sender_id = event['sender']['id']
    recipient_id = event['recipient']['id']
    message = event['message']

    # Indicates the message sent from the page itself
    is_echo = message.get('is_echo', False)
    if is_echo:
        return

    save_bot_user(SOURCE_FACEBOOK, sender_id)

    # Text of message
    message_text = message.get('text')

    if message_text:
        save_bot_message(SOURCE_FACEBOOK, message_text)
        message_text = message_text.lower().strip()

    message_attachments = message.get('attachments')

    if message_text:
        # If we receive a text message, check to see if it matches a keyword
        # and send back the example. Otherwise, just echo the text we received

        if any(t in message_text for t in [
            'hola', 'saludos', 'hello', 'hi',
        ]):
            bot.sendMessage(sender_id, 'Hola :smile: Soy SITP Bot')
            return
        if any(t in message_text for t in [
            'estación', 'estacion', 'parada', 'station', 'paradero',
        ]):
            bot.sendQuickReply(
                sender_id,
                'Por favor, envíame tu ubicación para poder '
                'la estación más cercana',
                [QuickReply('location')]
            )
            return

        # Try to get bus station or route
        if not send_bus_or_station_info(SOURCE_FACEBOOK, bot, sender_id, message_text):
            bot.sendMessage(
                sender_id,
                'Tienes que escribir el número de bus o de la parada. \n'
                'Por ejemplo, *18-2* o *033A06*'
            )
            bot.sendImage(sender_id, 'http://www.sitp.gov.co/modulos/Rutas/img/ParaderosPuntoParada.png')
            return
    elif message_attachments:
        for attachment in message_attachments:
            if attachment['type'] == 'image':
                bot.sendMessage(sender_id, 'Gracias por la foto ;) {}'.format(attachment['payload']['url']))
            elif attachment['type'] == 'audio':
                bot.sendMessage(sender_id, 'Gracias por el audio ;) {}'.format(attachment['payload']['url']))
            elif attachment['type'] == 'video':
                bot.sendMessage(sender_id, 'Gracias por el video ;) {}'.format(attachment['payload']['url']))
            elif attachment['type'] == 'file':
                bot.sendMessage(sender_id, 'Gracias por el archivo ;) {}'.format(attachment['payload']['url']))
            elif attachment['type'] == 'location':
                latitude = attachment['payload']['coordinates']['lat']
                longitude = attachment['payload']['coordinates']['long']
                bus_station = sitp_utils.get_closest_station(latitude, longitude)
                if bus_station:
                    bot.sendMessage(sender_id, 'Tu estación es más cercana es {}'.format(bus_station.name))
                else:
                    bot.sendMessage(sender_id, 'Estás muy lejos :(')

