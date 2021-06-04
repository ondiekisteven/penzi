from django.urls import path

from .views import save_message

urlpatterns = [
    path('', save_message, name='chat')
]
