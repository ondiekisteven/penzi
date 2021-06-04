from typing import Match
from django.contrib import admin

from .models import *


class MessageAdmin(admin.ModelAdmin):

    list_display = ('text', 'source', 'destination', 'type', 'date_created')
    search_fields = ('source', 'message')


admin.site.register(User)
admin.site.register(MatchRequest)
admin.site.register(CommandTrack)
admin.site.register(Message, MessageAdmin)
admin.site.register(UserDetails)
admin.site.register(UserDescription)
