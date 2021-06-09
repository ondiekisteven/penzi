from django.urls import path

from .views import save_message, dashboard, search_phone

urlpatterns = [
    path('messages/', dashboard, name='dashboard'),
    path('search/', search_phone, name='search-phone'),
]
