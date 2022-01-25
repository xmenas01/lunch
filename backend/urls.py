from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from lunch import views

router = routers.DefaultRouter()
router.register(r'restaurant', views.RestaurantViewSet, basename="restaurant")
router.register(r'user_points', views.UserPointsViewSet, basename="user_points")

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api-auth/', include('rest_framework.urls')),
                  path('', include(router.urls)),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
