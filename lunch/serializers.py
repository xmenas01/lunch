from rest_framework import serializers
from lunch import models
from rest_framework.exceptions import ValidationError
from decimal import Decimal
from datetime import date


class RestaurantSerializer(serializers.HyperlinkedModelSerializer):
    score = serializers.CharField(read_only=True)
    unique_users = serializers.CharField(read_only=True)

    # def to_representation(self, instance):
    #     resp = super().to_representation(instance)
    #     # import ipdb; ipdb.set_trace()
    #     today = date.today()
    #     f_date = self.context["request"].query_params.get("by_date", today)
    #     score = instance.get_score_by_date(date=f_date)
    #     resp["score"] = str(score)
    #     return resp


    class Meta:
        model = models.Restaurant
        fields = "__all__"


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
