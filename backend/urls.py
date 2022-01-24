from django.contrib import admin
from django.urls import path, include
from lunch import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'restaurant', views.RestaurantViewSet, basename="restaurant")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
