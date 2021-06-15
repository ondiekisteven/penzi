from api.serializers import MessageSerializer
from enum import Enum, IntEnum
from http.client import ACCEPTED

from rest_framework import serializers


class APIResponse:
    def __init__(self, status: int, message: str, reply=None) -> dict:
        if reply is None:
            self.reply = []
        else:
            self.reply = reply
        self.status = status
        self.message = message
        

    def data(self):
        response = {}
        response["status"]  = self.status
        response["message"] = self.message
        response["reply"]   = self.reply
        return response


class ResponseMessage(Enum):
    ACCEPTED = "Accepted for Processing"
    REJECTED = "Unknown message"

    @staticmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class ResponseCode(IntEnum):
    ACCEPTED = 0
    REJECTED = 1

    @staticmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class APIResponseSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    message = serializers.CharField(max_length=300)
    reply = MessageSerializer(many=True, required=False)

