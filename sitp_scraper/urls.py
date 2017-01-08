"""sitp_scraper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.contrib import admin

from .views import get_routes, get_route, RouteListView, RouteDetailView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^routes/$', RouteListView.as_view(), name='route_list'),
    url(r'^route/(?P<pk>\d+)/$', RouteDetailView.as_view(), name='route_detail'),
    url(r'^get_routes/$', get_routes, name='get_routes'),
    url(r'^get_route/(?P<pk>\d+)/$', get_route, name='get_route'),

    # Telegram bot
    url(r'^bot/', include('sitp_bot.urls', namespace='bot')),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', admin.site.urls),
]
