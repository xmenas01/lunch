from django.contrib import admin

from lunch.models import Restaurant, UserVote


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', "description")


class UserVoteAdmin(admin.ModelAdmin):
    list_display = ("restaurant", "user", "points", "date")


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(UserVote, UserVoteAdmin)
