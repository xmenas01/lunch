from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework import viewsets, status
from lunch import models
from lunch import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters
from lunch import filters


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RestaurantSerializer
    permission_classes = [IsAuthenticated | ReadOnly]
    filterset_class = filters.RestaurantFilter
    ordering = ["-score", "-unique_users", "name"]
    ordering_fields = "__all__"

    def get_queryset(self):
        if self.request.query_params and self.request.query_params.get("by_date"):
            date = self.request.query_params["by_date"]
            return models.Restaurant.objects.get_scores_by_date(date=date)

        return models.Restaurant.objects.get_scores()

# class RestaurantViewSet(viewsets.ModelViewSet):
#     queryset = models.Restaurant.objects.all()
#     serializer_class = serializers.RestaurantSerializer
#     permission_classes = [IsAuthenticated | ReadOnly]
#     filterset_class = filters.RestaurantFilter
#     # ordering = ["-days_score", "-unique_users"]
#     ordering_fields = "__all__"

    @action(detail=True, methods=["get", "post"])
    def vote(self, request, pk=None):
        user = request.user

        if request.method == "GET":
            points = user.votes.get_remaining_points()
            return Response({'remaining_points': points})

        restaurant = self.get_object()
        serializer = serializers.UserVoteSerializer(data={"user": user, "restaurant": restaurant})

        if serializer.is_valid():
            serializer.save()
            points = user.votes.get_remaining_points()
            return Response({'remaining_points': points})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
