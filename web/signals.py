from web.penzi import Penzi, Process
from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import CommandTrack, Message, MessageType, User, UserDescription, UserDetails, MessageCategory

import logging

logger = logging.getLogger(__name__)


# create UserDetails and UserDescription with empty details
@receiver(post_save, sender=User)
def create_details(sender, instance, created, **kwargs):
    if created:
        details = UserDetails.objects.create(user=instance)
        logger.info(details)
        desc = UserDescription.objects.create(user=instance)
        logger.info(desc)
        cmd_track = CommandTrack.objects.create(user=instance)
        logger.info(cmd_track)
