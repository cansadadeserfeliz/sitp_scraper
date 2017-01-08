from django.conf.urls import url

from django.views.generic import TemplateView

from .views import CommandReceiveView

urlpatterns = [
    url(
        r'^$',
        CommandReceiveView.as_view(),
        name='index',
    ),
]
