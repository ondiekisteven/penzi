from http.client import HTTPResponse
from json import dumps

import phonenumbers
from django.core.paginator import Paginator
from django.db.models import Count, Avg
from django.db.models.query_utils import Q
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from phonenumbers import NumberParseException

from web.models import Message, MessageType, User
from django.shortcuts import redirect, render


def dashboard(request):
    # CHECK IF THERE IS A PHONE SEARCH
    if request.method == 'POST':
        phone = request.POST['table_search']
        if phone.isnumeric:
            phone = int(phone)
            all_messages = Message.objects.filter(Q(source=phone) | Q(destination=phone))
        else:
            return redirect('dashboard')
    else:
        all_messages = Message.objects.all()

    # FILTER MESSAGES
    flter = request.GET.get('filter')
    if flter:
        messages = all_messages.filter(type=flter)
    else:
        messages = all_messages.all().order_by('-id')

    # PASS THROUGH PAGINATOR
    p = Paginator(messages, 15)
    page = request.GET.get('page')

    if page and page.isnumeric():
        page_messages = p.get_page(page)
    else:
        page_messages = p.get_page(1)

    today_messages = messages.filter(date_created__date=timezone.now().date()).count()
    # hourly_average = messages.values('date_created__hour').annotate(Count("date_created__hour")).aggregate(Avg('date_created__hour__count'))
    time = timezone.now() - Message.objects.first().date_created
    hours = int((time.days * 24) + (time.seconds / 3600))
    hourly_average = hours / messages.count()
    context = {
        'all_messages': messages.count(),
        'sent_messages': messages.filter(type=MessageType.OUTGOING).count(),
        'received': messages.filter(type=MessageType.INCOMING).count(),
        'latest_messages': page_messages,
        'today_messages': today_messages,
        'hourly_average': hourly_average,
    }
    return render(request, 'web/dashboard.html', context)


def search_phone(request):
    if request.is_ajax():
        query = request.GET.get('q', '')

        users = User.objects.filter(phone__icontains=query)
        result = []
        for m in users:
            result.append(str(m.phone))
        data = dumps(result)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)


def save_message(request):

    phone = request.GET.get('phone')
    try:
        number = phonenumbers.format_number(
            phonenumbers.parse(phone, 'KE'),
            phonenumbers.PhoneNumberFormat.E164
        )[1:]
    except NumberParseException:
        return render(request, 'web/chat.html')

    if request.method == 'POST':
        if not phone:
            return redirect('chat')
        ###########################################
        text = request.POST["text"]

        # save incoming message to messages table
        message = Message()
        message.text = text
        message.source = number
        message.destination = "1234"  # shortcode
        message.type = MessageType.INCOMING
        message.save()
        ###########################################
        return redirect('{}?phone={}'.format(reverse('chat'), number))
    if phone:
        messages = Message.objects.filter(Q(source=number) | Q(destination=number))
        last = messages.last()
    else:
        messages = None
        last = None

    context = {
        'messages': messages,
        'latest': last
    }
    return render(request, 'web/chat.html', context)
