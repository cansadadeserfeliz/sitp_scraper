from django.conf.urls import url

from django.views.generic import TemplateView

from .views import CommandReceiveView

urlpatterns = [
    url(
        r'(?P<bot_token>.+)/$',
        CommandReceiveView.as_view(),
        name='index',
    ),
]
