from web.penzi import Penzi, Process
from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import CommandTrack, Message, MessageType, User, UserDescription, UserDetails, MessageCategory


def send_search_notification(searching: Message, searched: User):
    searching_user = User.objects.filter(phone=searching.source)
    if searching_user.exists():
        searching_user = searching_user.first()
        if searching_user.gender == "male":
            title = "lady"
            pronoun = "her"
            refer = "her"
        else:
            title = "gent"
            pronoun = "him"
            refer = "his"
        Message.objects.create(
            text=f"Hi {searched.full_name}, a {title} named {searching_user.full_name} is interested in you and has "
                 f"requested your details, aged {searching_user.age} based in {searching_user.town}. Do you want to "
                 f"know more about {pronoun}? Reply with YES to get more details about {refer}",
            type=MessageType.OUTGOING,
            source=1234,
            destination=searched.phone
        )


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
        penzi = Penzi(instance)
        penzi_reply = penzi.validate()
        print(f"PENZI REPLY: {penzi_reply}")
        if 'category' in penzi_reply:

            reply = Process(penzi_reply).process()
            print(f"PROCESSING REPLY: {reply}")

            if reply['action'] == "reply":

                # loop through and send all messages
                for message in reply["messages"]:
                    Message.objects.create(
                        text=message,
                        type=MessageType.OUTGOING,
                        source=1234,
                        destination=instance.source
                    )
                if penzi_reply["category"] == MessageCategory.DESCRIPTION_REQUEST and 'searched_user' in reply:

                    # if user is requesting description, send notification to the searched user
                    notif_user = reply['searched_user']
                    send_search_notification(instance, notif_user)
            else:
                pass
        else:
            if penzi.category() != MessageCategory.SERVICE_REGISTRATION:
                return
            # only reply with invalid input message to unregistered users if they are trying to register
            Message.objects.create(
                text=penzi_reply["desc"],
                type=MessageType.OUTGOING,
                source=1234,
                destination=instance.source
            )
