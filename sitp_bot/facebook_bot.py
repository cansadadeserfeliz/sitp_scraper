import requests
import logging
from django.conf import settings

from .models import SOURCE_FACEBOOK
from .utils import save_bot_user, save_bot_message
from sitp_scraper import utils as sitp_utils

logger = logging.getLogger('facebook.bot')


def call_send_api(message_data):
    response = requests.post(
        'https://graph.facebook.com/v2.6/me/messages?access_token={}'.format(settings.FACEBOOK_PAGE_ACCESS_TOKEN),
        json=message_data,
    )
    if response.status_code == 200:
        response_body = response.json()
        recipient_id = response_body['recipient_id']
        message_id = response_body['message_id']
    else:
        logger.error('Unable to send message. Status code: {}'.format(response.status_code))


def send_generic_message(
        recipient_id,
        message_text=
        'Hola, soy SITP bot. Envíame el código de bus que estás buscando o '
        'tu ubicación para encontrar el paradero más cercano.',
        command=None,
        quick_replies=[],
        attachment={},
):
    message_data = {
        'recipient': {
            'id': recipient_id,
        },
        'message': {
            'text': message_text,
        },
    }
    if quick_replies:
        message_data['message']['quick_replies'] = quick_replies
    if attachment:
        message_data['message']['attachment'] = attachment
    call_send_api(message_data)


def received_message(event):
    sender_id = event['sender']['id']
    recipient_id = event['recipient']['id']
    message = event['message']

    # Indicates the message sent from the page itself
    is_echo = message.get('is_echo', False)
    if is_echo:
        return

    # Text of message
    message_text = message.get('text')

    message_attachments = message.get('attachments')

    save_bot_user(SOURCE_FACEBOOK, sender_id)

    if message_text:
        save_bot_message(SOURCE_FACEBOOK, message_text)
        # If we receive a text message, check to see if it matches a keyword
        # and send back the example. Otherwise, just echo the text we received

        route = sitp_utils.get_route(message_text)

        if route:
            send_generic_message(sender_id, '''
            {code} {name} es una ruta {route_type}.
            Aquí {map_link} puedes encontrar el mapa de la ruta.
            '''.format(
                code=route.code,
                name=route.name,
                route_type=route.get_route_type_display(),
                map_link=route.map_link,
            ))
            return

        if any(t in message_text.lower() for t in [
            'hola', 'saludos', 'hello', 'hi',
        ]):
            send_generic_message(sender_id)
            return
        if any(t in message_text.lower() for t in [
            'estación', 'estacion', 'parada', 'station', 'paradero',
        ]):
            send_generic_message(
                sender_id,
                'Por favor, envíame tu ubicación para poder la estación más cercana',
                quick_replies=[{'content_type': 'location'},
            ])
            return
        else:
            send_generic_message(
                sender_id, 'Hola, soy SITP Bot y estoy aprendiendo cosas :)')
    elif message_attachments:
        for attachment in message_attachments:
            if attachment['type'] == 'image':
                send_generic_message(sender_id, 'Gracias por la foto ;) {}'.format(attachment['payload']['url']))
            elif attachment['type'] == 'audio':
                send_generic_message(sender_id, 'Gracias por el audio ;) {}'.format(attachment['payload']['url']))
            elif attachment['type'] == 'video':
                send_generic_message(sender_id, 'Gracias por el video ;) {}'.format(attachment['payload']['url']))
            elif attachment['type'] == 'file':
                send_generic_message(sender_id, 'Gracias por el archivo ;) {}'.format(attachment['payload']['url']))
            elif attachment['type'] == 'location':
                latitude = attachment['payload']['coordinates']['lat']
                longitude = attachment['payload']['coordinates']['long']
                bus_station = sitp_utils.get_closest_station(latitude, longitude)
                if bus_station:
                    send_generic_message(sender_id, 'Tu estación es más cercana es {}'.format(bus_station.name))
                else:
                    send_generic_message(sender_id, 'Estás muy lejos :(')

