from django.contrib import admin

from .models import BotUser, BotUserRequestStats, MessageStats


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = (
        'chat_user_id',
        'source',
        'first_name',
        'last_name',
        'username',
        'timezone',
        'locale',
        'requests_count',
        'created_at',
        'updated_at',
    )
    search_fields = ('chat_user_id', 'first_name', 'last_name')
    list_filter = ('source', )

@admin.register(BotUserRequestStats)
class BotUserRequestStatsAdmin(admin.ModelAdmin):
    list_display = (
        'bot_user',
        'requests_count',
        'day',
    )
    search_fields = ('bot_user',)


@admin.register(MessageStats)
class MessageStatsAdmin(admin.ModelAdmin):
    list_display = (
        'phrase',
        'source',
        'requests_count',
        'created_at',
        'updated_at',
    )
    search_fields = ('bot_user',)
    list_filter = ('source', )
