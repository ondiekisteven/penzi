import phonenumbers
from django.db.models.query_utils import Q
from django.urls import reverse
from phonenumbers import NumberParseException

from web.models import Message, MessageType
from django.shortcuts import redirect, render


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
