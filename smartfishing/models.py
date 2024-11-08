from datetime import timedelta

from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point as BasePoint
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from smartfishing.constants import (
    BASE_COORDINATES,
    CUTOFF_DATE,
    DESCRIPTION_LEN,
    FORBIDDEN_ZONE_NAME_LEN,
    MONTHS_UNTIL_ARCHIVE,
    POINT_NAME_LEN,
    POINT_TYPE_LEN,
    POINT_TYPES,
    RATING,
    REPORT_TYPES,
)
from smartfishing.mixins import CreatedAndUpdatedDateMixin
from users.models import User


class PointManager(models.Manager):
    def to_archive_inactive_points(self):
        cutoff_date = timezone.now() - timedelta(days=CUTOFF_DATE)
        potential_points = (
            self.filter(is_active=True)
            .filter(Q(comments__created_at__lt=cutoff_date))
            .distinct()
        )
        potential_points.update(is_active=False)


class Point(gis_models.Model):
    objects = PointManager()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="points",
        verbose_name="Автор",
    )
    name = models.CharField(
        "Наименование",
        max_length=POINT_NAME_LEN,
        unique=True,
    )
    type = models.CharField(
        "Тип",
        choices=tuple(POINT_TYPES.items()),
        max_length=POINT_TYPE_LEN,
        default="fishing",
    )
    image = models.ImageField(
        "Картинка",
        upload_to="point_images/%d_%m_%Y/",
        null=True,
        blank=True,
    )
    coordinates = gis_models.PointField(
        "Координаты",
        geography=True,
        unique=True,
        srid=4326,
        default=BasePoint(*BASE_COORDINATES),
    )
    description = models.CharField(
        "Описание",
        max_length=DESCRIPTION_LEN,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        "Дата обновления",
        auto_now=True,
    )
    is_active = models.BooleanField(
        "Активный",
        default=True,
    )

    class Meta:
        verbose_name = "Координаты"
        verbose_name_plural = "Координаты"
        ordering = ("-updated_at", "is_active")
        constraints = [
            models.UniqueConstraint(
                fields=("user", "coordinates"),
                name="invalid_owner_coordinates_unique",
            )
        ]

    def as_geojson(self):
        return {
            "type": "Point",
            "coordinates": [self.coordinates.x, self.coordinates.y],
        }

    def __str__(self):
        return self.name


class PointRating(models.Model):
    point = models.ForeignKey(
        Point,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    rating = models.PositiveSmallIntegerField(
        choices=tuple(RATING.items()),
    )
    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Рейтинг точки"
        verbose_name_plural = "Рейтинги точек"
        constraints = [
            models.UniqueConstraint(
                fields=("point", "user"),
                name="invalid_rating_error",
            )
        ]

    def __str__(self):
        return f"Рейтинг {self.rating} -> {self.point.name}"


class Comment(CreatedAndUpdatedDateMixin):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    point = models.ForeignKey(
        Point,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Координаты",
    )
    message = models.TextField(
        "Текст сообщения",
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"{self.point}"


class Equipment(models.Model):
    point = models.ForeignKey(
        Point,
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=30,
        verbose_name="Инструмент",
        default="Снасти",
    )


class Fish(models.Model):
    point = models.ForeignKey(
        Point,
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=30,
        verbose_name="Вид рыбы",
    )


class FavoritePoint(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owner_favorite_points",
        verbose_name="Пользователь",
    )
    point = models.ForeignKey(
        Point,
        on_delete=models.CASCADE,
        related_name="coord_in_favorite",
        verbose_name="Координаты",
    )

    class Meta:
        verbose_name = "Избранные координаты"
        verbose_name_plural = "Избранные координаты"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "point"),
                name="uniq_favorite_user_point",
            ),
        )

    def __str__(self):
        return f"{self.user} -> {self.point}"


class ForbiddenZone(models.Model):
    name = models.CharField(
        "Название",
        max_length=FORBIDDEN_ZONE_NAME_LEN,
    )
    boundary = gis_models.PolygonField(
        "Зона",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Запрещенная зона"
        verbose_name_plural = "Запрещенные зоны"
        ordering = ("name",)


class ArchiveSetting(models.Model):
    months_until_archive = models.PositiveIntegerField(
        "Месяцев до архивации",
        default=MONTHS_UNTIL_ARCHIVE,
    )

    class Meta:
        ordering = ("months_until_archive",)
        verbose_name = "Настройки времени архивации точек"
        verbose_name_plural = "Настройки времени архивации точек"

    def clean(self):
        if self.months_until_archive == 0:
            raise ValidationError("Укажите натуральное число")

    def __str__(self):
        return (
            f"{self.months_until_archive} "
            f"{'месяца' if self.months_until_archive < 5 else 'месяцев'} "
            "до архивации"
        )


class Report(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name="Пользователь",
    )
    point = models.ForeignKey(
        Point,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name="Точка",
    )
    description = models.TextField(
        "Описание жалобы",
    )
    type = models.CharField(
        "Тип",
        choices=tuple(REPORT_TYPES.items()),
    )
    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-created_at", "type")
        verbose_name = "Жалоба"
        verbose_name_plural = "Жалобы"

    def __str__(self):
        return f"Жалоба от {self.user.username} на {self.point.name}"
