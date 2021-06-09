from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from web.models import User as PenziUser
from accounts.forms import UserRegistrationForm


def create_user(request):
    form = UserRegistrationForm()
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            messages.success(request, f"User '{username}' created successfully")
            form.save()
            return redirect('dashboard')
        else:
            messages.warning(request, form.errors)

    context = {
        'form': form,
    }
    return render(request, 'accounts/create_user.html', context)


def users(request):
    admins = User.objects.all()
    penzi_users = PenziUser.objects.all()

    context = {
        'admins': admins,
        'penzi_users': penzi_users,
    }
    return render(request, 'accounts/users.html', context)
