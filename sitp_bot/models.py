from django.db import models

SOURCE_FACEBOOK = 1
SOURCE_TELEGRAM = 2


class BotUser(models.Model):
    source = models.PositiveSmallIntegerField(choices=[
        (SOURCE_FACEBOOK, 'Facebook'),
        (SOURCE_TELEGRAM, 'Telegram'),
    ])
    chat_user_id = models.CharField(max_length=50)
    first_name = models.CharField(max_length=150, default='')
    last_name = models.CharField(max_length=150, default='')
    timezone = models.SmallIntegerField(null=True)
    locale = models.CharField(max_length=10, default='')
    requests_count = models.BigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {} {}'.format(
            self.chat_user_id,
            self.first_name,
            self.last_name,
        ).strip()

    class Meta:
        verbose_name = 'Bot User'
        verbose_name_plural = 'Bot Users'
        unique_together = ('source', 'chat_user_id')
        ordering = ['-updated_at']


class BotUserRequestStats(models.Model):
    bot_user = models.ForeignKey('sitp_bot.BotUser')
    requests_count = models.BigIntegerField(default=0)
    day = models.DateField()

    class Meta:
        verbose_name = 'Bot User stats'
        verbose_name_plural = 'Bot User stats'
        unique_together = ('bot_user', 'day')
        ordering = ['-day', '-requests_count']


class MessageStats(models.Model):
    source = models.PositiveSmallIntegerField(choices=[
        (SOURCE_FACEBOOK, 'Facebook'),
        (SOURCE_TELEGRAM, 'Telegram'),
    ])
    phrase = models.CharField(max_length=500)
    requests_count = models.BigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bot Messages Stats'
        verbose_name_plural = 'Bot Messages Stats'
        unique_together = ('source', 'phrase')
        ordering = ['-requests_count']
