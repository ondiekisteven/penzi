from web.penzi import parse_message
import phonenumbers
import logging

from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

from web.models import Message
from api.serializers import MessageSerializer


logger = logging.getLogger(__name__)

class MessagesList(APIView):
    """
    Get all messages, Create new Message
    """
    def get(self, request, format=None):
        messages = Message.objects.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save()
            response = parse_message(message)
            response_serializer = MessageSerializer(response, many=True)
            logger.info(f"RESPONSE SERIALIZER: {repr(response_serializer)}")
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserMessages(APIView):
    def validate_phone(self, phone):
        try:
            number = phonenumbers.format_number(
                phonenumbers.parse(phone, 'KE'),
                phonenumbers.PhoneNumberFormat.E164
            )[1:]
            return number
        except phonenumbers.NumberParseException:
            return None

    def get(self, request, phone, format=None):
        number = self.validate_phone(phone)
        if number is None:
            return Response({"error": "Invalid phone"}, status=status.HTTP_400_BAD_REQUEST)
        messages = Message.objects.filter(Q(source=number) | Q(destination=number))
        print(f"{'*'*20}\n\n\n")
        print(f"{messages}")
        print(f"{'*'*20}\n\n\n")
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
