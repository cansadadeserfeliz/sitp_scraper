from django.template.loader import render_to_string

from python_bot_utils.telegram import send_markdown_message


def send_help_message(bot, chat_id, first_name=''):
    send_markdown_message(bot, chat_id, render_to_string('bot/help.html', dict(
        first_name=first_name,
    )))
