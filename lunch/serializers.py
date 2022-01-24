from decimal import Decimal

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from lunch import models


class RestaurantSerializer(serializers.HyperlinkedModelSerializer):
    score = serializers.CharField(read_only=True)
    unique_users = serializers.CharField(read_only=True)

    class Meta:
        model = models.Restaurant
        fields = ("url", "name", "score", "unique_users", "description")


class UserVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserVote
        fields = "__all__"

    def to_internal_value(self, data):
        user = data["user"]
        restaurant = data["restaurant"]
        count = user.votes.get_restaurant_votes(restaurant=restaurant).count()

        if count == 0:
            points = 1
        elif count == 1:
            points = 0.5
        else:
            points = 0.25
        data["points"] = points

        return data

    def validate(self, data):
        points = data["points"]
        user = data["user"]
        user_points = user.votes.get_remaining_points()

        if user_points - Decimal(points) <= 0:
            raise ValidationError("out of points")

        return super().validate(data)
