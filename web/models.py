from enum import IntEnum

from django.db import models


class MessageType(IntEnum):
    
    INCOMING = 0
    OUTGOING = 1

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class MessageCategory(IntEnum):

    SERVICE_ACTIVATION = 1
    SERVICE_REGISTRATION = 2
    DETAILS_REGISTRATION = 3
    SELF_DESCRIPTION = 4
    MATCH_REQUEST = 5
    SUBSEQUENT_MATCH = 6
    MORE_DETAILS = 7
    DESCRIPTION_REQUEST = 8
    NOTICE_CONFIRMATION = 9
    RE_ACTIVATION = 10

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class User(models.Model):
    phone = models.BigIntegerField(unique=True)
    full_name = models.CharField(max_length=150)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    county = models.CharField(max_length=100)
    town = models.CharField(max_length=200)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_use = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone}"


class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    education = models.CharField(max_length=200)
    profession = models.CharField(max_length=200)
    marital_status = models.CharField(max_length=20)
    religion = models.CharField(max_length=50)
    tribe = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.phone} details"
    
    class Meta:
        verbose_name_plural = 'User Details'


class UserDescription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return f"{self.user.phone} description"


class MatchRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lower_age = models.IntegerField(blank=True, null=True)
    upper_age = models.IntegerField()
    town = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)
    page = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.phone} request"


class Command(models.Model):
    command_name = models.CharField(max_length=100)
    command_desc = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.command_name}"


class CommandTrack(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    command = models.IntegerField(choices=MessageCategory.choices(), default=MessageCategory.SERVICE_REGISTRATION)
    user_reply = models.CharField(max_length=200, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.phone}"


class Message(models.Model):
    text = models.CharField(max_length=200)
    type = models.IntegerField(choices=MessageType.choices())  # incoming/outgoing
    source = models.BigIntegerField()
    destination = models.BigIntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
