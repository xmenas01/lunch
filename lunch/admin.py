from django.contrib import admin

from lunch.models import Restaurant, UserVote

admin.site.register(Restaurant)
admin.site.register(UserVote)
