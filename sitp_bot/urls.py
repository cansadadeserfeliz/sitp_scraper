from django.conf.urls import url

from django.views.generic import TemplateView

from .views import CommandReceiveView, FacebookCommandReceiveView

urlpatterns = [
    url(
        r'(?P<bot_token>.+)/$',
        CommandReceiveView.as_view(),
        name='index',
    ),


    url(
        r'fb-webhook/(?P<bot_keyword>.+)/$',
        FacebookCommandReceiveView.as_view(),
        name='fb_webhook',
    ),
]
