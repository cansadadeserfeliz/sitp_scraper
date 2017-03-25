import requests

from django.conf import settings
from django.utils import timezone

from .models import SOURCE_FACEBOOK
from .models import BotUser, BotUserRequestStats, MessageStats


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
