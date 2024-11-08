from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import CommentViewSet, FavoritePointViewSet, PointViewSet

router_v1 = DefaultRouter()

router_v1.register(r"points", PointViewSet, basename="points")
router_v1.register(
    r"points/(?P<id>\d+)/comments", CommentViewSet, basename="comments"
)
router_v1.register(
    r"points/(?P<point_id>\d+)/favorites",
    FavoritePointViewSet,
    basename="favorites",
)

urlpatterns = [
    path("v1/", include(router_v1.urls)),
]
