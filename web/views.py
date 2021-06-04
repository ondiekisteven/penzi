from django.db.models.query_utils import Q
from django.urls import reverse

from web.models import Message, MessageType
from django.shortcuts import redirect, render


def save_message(request):

    phone = request.GET.get('phone')

    if request.method == 'POST':
        ###########################################
        text = request.POST["text"]

        # save incoming message to messages table
        message = Message()
        message.text = text
        message.source = phone
        message.destination = "1234"  # shortcode
        message.type = MessageType.INCOMING
        message.save()
        ###########################################
        return redirect('{}?phone={}'.format(reverse('chat'), phone))
    if phone:
        messages = Message.objects.filter(Q(source=phone) | Q(destination=phone))
        last = messages.last()
    else:
        messages = None
        last = None

    context = {
        'messages': messages,
        'latest': last
    }
    return render(request, 'web/chat.html', context)
