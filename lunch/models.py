from datetime import date

from constance import config
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum, Count


class RestaurantManager(models.Manager):
    def get_scores(self):
        qs = self.get_queryset()
        ann_qs = qs.annotate(score=Sum("votes__points", default=0), unique_users=Count("votes__user", distinct=True))
        return ann_qs

    def get_scores_by_date(self, date):
        qs = self.get_queryset().filter(votes__date__lte=date)
        ann_qs = qs.annotate(score=Sum("votes__points"), unique_users=Count("votes__user", distinct=True))
        return ann_qs


class Restaurant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    objects = RestaurantManager()

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class UserVoteManager(models.Manager):

    def get_restaurant_votes(self, restaurant):
        return self.get_queryset().filter(user=self.instance, restaurant=restaurant)

    def get_todays_votes(self):
        today = date.today()
        if isinstance(self.instance, User):
            return self.get_queryset().filter(date=today, user=self.instance)
        if isinstance(self.instance, Restaurant):
            return self.get_queryset().filter(date=today, restaurant=self.instance)

    def get_remaining_points(self):
        points = self.get_todays_votes().aggregate(Sum("points"))["points__sum"] or 0
        return config.USER_MAX_POINTS - points


class UserVote(models.Model):
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="votes", on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, related_name="votes", on_delete=models.CASCADE)
    points = models.DecimalField(default=0, max_digits=5, decimal_places=2)

    objects = UserVoteManager()

    class Meta:
        ordering = ("-date",)

    def __str__(self):
        return f"{self.user} voted for {self.restaurant}"
