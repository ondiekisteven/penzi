from django.urls import path

from.views import MessagesList, UserMessages


urlpatterns = [
    path('messages/', MessagesList.as_view()),
    path('messages/<str:phone>/', UserMessages.as_view())
]
