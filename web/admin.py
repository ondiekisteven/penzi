from typing import Match
from django.contrib import admin

from .models import *


class MessageAdmin(admin.ModelAdmin):

    list_display = ('text', 'source', 'destination', 'type', 'date_created')
    search_fields = ('source', 'message')
    list_filter = ('type',)


class UserAdmin(admin.ModelAdmin):

    list_display = ('phone', 'full_name', 'age', 'gender', 'town', 'county')
    search_fields = ('phone', 'full_name')
    list_filter = ('gender',)


class MatchRequestAdmin(admin.ModelAdmin):

    list_display = ('user', 'lower_age', 'upper_age', 'town',)
    search_fields = ('user__phone', 'user__full_name')


admin.site.register(User, UserAdmin)
admin.site.register(MatchRequest, MatchRequestAdmin)
admin.site.register(CommandTrack)
admin.site.register(Message, MessageAdmin)
admin.site.register(UserDetails)
admin.site.register(UserDescription)
