from django.conf.urls import url


from .views import TelegramCommandReceiveView, FacebookCommandReceiveView

urlpatterns = [
    url(
        r'fb-webhook/(?P<bot_keyword>.+)/$',
        FacebookCommandReceiveView.as_view(),
        name='fb_webhook',
    ),

    url(
        r'(?P<bot_token>.+)/$',
        TelegramCommandReceiveView.as_view(),
        name='telegram_webhook',
    ),
]
