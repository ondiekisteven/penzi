from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .forms import UserLoginForm
from .views import create_user, users


urlpatterns = [
    path('login/', LoginView.as_view(
        template_name='accounts/login.html',
        authentication_form=UserLoginForm), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', users, name='users'),
    path('users/add/', create_user, name='create-user'),
]
