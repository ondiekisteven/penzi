import phonenumbers
import logging

from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.utils import APIResponse, APIResponseSerializer, ResponseCode, ResponseMessage
from web.penzi import parse_message
from web.models import Message
from api.serializers import MessageSerializer


logger = logging.getLogger(__name__)


def validate_phone(phone):
    try:
        number = phonenumbers.format_number(
            phonenumbers.parse(phone, 'KE'),
            phonenumbers.PhoneNumberFormat.E164
        )[1:]
        return number
    except phonenumbers.NumberParseException:
        return None


class MessagesList(APIView):
    """
    Get all messages, Create new Message
    """
    def get(self, request, format=None):
        messages = Message.objects.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        # convert phone to international format incase it's not
        request_data = request.data
        try:
            phone = request_data["source"]
        except Exception as x:
            rsp = APIResponse(status=ResponseCode.REJECTED, message=str(x))
            return Response(APIResponseSerializer(rsp).data, status=status.HTTP_400_BAD_REQUEST)
        validated_ = validate_phone(str(phone))

        # Check if phone is valid, return error message if not
        if validated_ is None:
            rsp = APIResponse(
                status=ResponseCode.REJECTED, 
                message="Invalid phone"
            ).data()
            return Response(rsp, status=status.HTTP_400_BAD_REQUEST)
        request_data["source"] = validated_

        serializer = MessageSerializer(data=request_data)
        if serializer.is_valid():
            logger.debug(f"REQUEST DATA: {request_data}")
            message = serializer.save()

            # Get response from Engine
            response = parse_message(message)
            print(f"#############################{response}")

            # if response is empty, then return code 1, unknown message
            if not response:
                rsp = APIResponse(status=ResponseCode.ACCEPTED,message="Unknown message",)
                return Response(APIResponseSerializer(rsp).data, status=status.HTTP_200_OK)

            # else return response code 0, accepted
            response_serializer = MessageSerializer(response, many=True)
            rsp = APIResponse(status=ResponseCode.ACCEPTED,message=ResponseMessage.ACCEPTED, reply=response)
            return Response(APIResponseSerializer(rsp).data, status=status.HTTP_201_CREATED)
        
        # incase serializer encounters errors
        rsp = APIResponse(status=ResponseCode.REJECTED, message=serializer.errors)
        return Response(APIResponseSerializer(rsp).data, status=status.HTTP_400_BAD_REQUEST)


class UserMessages(APIView):
    

    def get(self, request, phone, format=None):
        number = validate_phone(phone)
        if number is None:
            return Response({"error": "Invalid phone"}, status=status.HTTP_400_BAD_REQUEST)
        messages = Message.objects.filter(Q(source=number) | Q(destination=number))
        print(f"{'*'*20}\n\n\n")
        print(f"{messages}")
        print(f"{'*'*20}\n\n\n")
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)














# "status": 0,                  # 0 for success, other for error
# "message": "accepted"         # accepted for code 0, unknown message for other cde
# "reply": {
#         "id": 6,
#         "text": "message body",
#         "type": 1, 
#         "source": 1234,
#         "destination": 254745022222,
#         "date_created": "2021-06-11T11:19:47.323014+03:00"
#     }