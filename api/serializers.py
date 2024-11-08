import json

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point as BasePoint
from django.core.exceptions import ValidationError
from rest_framework import serializers

from smartfishing.models import Comment, FavoritePoint, ForbiddenZone, Point

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "user", "point", "message", "created_at", "updated_at")
        read_only_fields = ("user", "point", "created_at", "updated_at")


class PointSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Point
        fields = (
            "id",
            "user",
            "name",
            "type",
            "image",
            "as_geojson",
            "description",
            "comments",
            "created_at",
            "updated_at",
            "is_active",
        )
        read_only_fields = (
            "created_at",
            "updated_at",
            "user",
            "is_active",
        )

    def is_point_in_forbidden(self, latitude, longitude):
        point = BasePoint(longitude, latitude)
        for zone in ForbiddenZone.objects.all():
            if zone.boundary.contains(point):
                return True
        return False

    def validate(self, data):
        as_geojson = json.loads(self.initial_data.get("as_geojson"))
        longitude, latitude = as_geojson.get("coordinates")
        if self.is_point_in_forbidden(latitude, longitude):
            raise ValidationError(
                "Добавление точек в этой области запрещено. "
                f"Координаты: {longitude}, {latitude}"
            )
        return data

    def create(self, validated_data):
        as_geojson = json.loads(self.initial_data.get("as_geojson"))
        longitude, latitude = as_geojson.get("coordinates")
        coordinates = BasePoint(longitude, latitude)

        validated_data["user"] = self.context.get("request").user
        validated_data["coordinates"] = GEOSGeometry(
            json.dumps(
                {
                    "type": "Point",
                    "coordinates": [coordinates.x, coordinates.y],
                }
            )
        )

        return super().create(validated_data)

    def update(self, instance, validated_data):
        as_geojson = json.loads(self.initial_data.get("as_geojson"))
        longitude, latitude = as_geojson.get("coordinates")
        coordinates = BasePoint(longitude, latitude)

        instance.coordinates = GEOSGeometry(
            json.dumps(
                {
                    "type": "Point",
                    "coordinates": [coordinates.x, coordinates.y],
                }
            )
        )
        instance.name = validated_data.get("name", instance.name)
        instance.type = validated_data.get("type", instance.type)
        instance.image = validated_data.get("image", instance.image)
        instance.description = validated_data.get(
            "description", instance.description
        )

        instance.save()
        return instance


class FavoritePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoritePoint
        fields = ("user", "point")
        read_only_fields = ("user", "point")
