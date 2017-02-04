import requests
import logging
from django.conf import settings

logger = logging.getLogger('facebook.bot')


def get_user_info(user_id):
    response = requests.get(
        'https://graph.facebook.com/v2.6/{user_id}'
        '?fields=first_name,last_name,profile_pic,locale,timezone,gender'
        '&access_token={access_token}'.format(
            user_id=user_id,
            access_token=settings.FACEBOOK_PAGE_ACCESS_TOKEN,
        )
    )
    user_info = response.json()
    logger.info('FB user', extra=user_info)
    #{
    #   "first_name": "Pepito",
    #   "last_name": "Perez",
    #   "profile_pic": "",
    #   "locale": "en_GB",
    #   "timezone": -5,
    #   "gender": "female"
    #}


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
        message_text='Hola, soy SITP bot',
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
    time_of_message = event['timestamp']
    message = event['message']
    message_id = message['mid']
    message_text = message.get('text')
    message_attachments = message.get('attachments')

    if message_text:
        # If we receive a text message, check to see if it matches a keyword
        # and send back the example. Otherwise, just echo the text we received
        if message_text == 'generic':
            send_generic_message(sender_id)
            return
        else:
            send_generic_message(sender_id, 'Hola, soy SITP Bot y estoy aprendiendo cosas :)')
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
