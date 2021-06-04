from web.penzi import Penzi, Process
from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import CommandTrack, Message, MessageType, User, UserDescription, UserDetails


# create UserDetails and UserDescription with empty details
@receiver(post_save, sender=User)
def create_details(sender, instance, created, **kwargs):
    if created:
        UserDetails.objects.create(user=instance)
        UserDescription.objects.create(user=instance)
        CommandTrack.objects.create(user=instance)


# signal for processing a message after it has been create
@receiver(post_save, sender=Message)
def parse_message(sender, instance, created, **kwargs):
    if created:
        if instance.source == 1234:
            return
        penzi_reply = Penzi(instance).validate()

        if 'category' in penzi_reply:
            reply = Process(penzi_reply).process()
            if reply['action'] == "reply":
                for message in reply["messages"]:
                    Message.objects.create(
                        text=message,
                        type=MessageType.OUTGOING,
                        source=1234,
                        destination=instance.source
                    )
            else:
                pass
        else:
            Message.objects.create(
                text=penzi_reply["desc"],
                type=MessageType.OUTGOING,
                source=1234,
                destination=instance.source
            )
