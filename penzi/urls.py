"""penzi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from accounts import urls as acc_urls

from web import urls
from web.views import save_message, messages_list, user_messages
from api import urls as api_urls

from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('messages/', save_message, name='chat'),
    path('admin/', admin.site.urls),
    path('dashboard/', include(urls)),
    path('accounts/', include(acc_urls)),
    path('api/v1/', include(api_urls)),
    path('api/messages/', messages_list),
    path('api/messages/<str:phone>/', user_messages),
]

urlpatterns = format_suffix_patterns(urlpatterns)
