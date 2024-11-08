from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsTouristPoint
from api.serializers import (
    CommentSerializer,
    FavoritePointSerializer,
    PointSerializer,
)
from smartfishing.models import Comment, FavoritePoint, Point


class PointViewSet(viewsets.ModelViewSet):
    serializer_class = PointSerializer
    permission_classes = (IsAuthenticated & IsTouristPoint,)

    def get_queryset(self):
        return Point.objects.filter(is_active=True)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=request.user,
            point=get_object_or_404(Point, id=self.kwargs.get("id")),
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FavoritePointViewSet(viewsets.ModelViewSet):
    queryset = FavoritePoint.objects.all()
    serializer_class = FavoritePointSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
