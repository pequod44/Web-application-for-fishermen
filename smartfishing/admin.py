from datetime import timedelta

from django.contrib import admin
from django.contrib.gis import admin as gis_admin
from django.utils import timezone

from smartfishing.models import (
    ArchiveSetting,
    Comment,
    Equipment,
    FavoritePoint,
    Fish,
    ForbiddenZone,
    Point,
    PointRating,
    Report,
)


@admin.register(Point)
class PointAdmin(gis_admin.GISModelAdmin):
    list_display = (
        "name",
        "coordinates",
        "type",
        "user",
        "description",
        "updated_at",
        "is_active",
    )
    list_filter = ("type", "is_active")
    search_fields = (
        "name",
        "description",
    )
    readonly_fields = ("created_at", "updated_at")
    fields = (
        "name",
        "coordinates",
        "type",
        "user",
        "description",
        "image",
        "created_at",
        "updated_at",
        "is_active",
    )

    actions = ["archive_points"]

    def archive_points(self, request, queryset):
        archive_setting = ArchiveSetting.objects.first()
        if not archive_setting:
            self.message_user(
                request,
                "Настройка времени архивации не установлена.",
                level="error",
            )
            return

        archive_date = timezone.now() - timedelta(
            days=archive_setting.months_until_archive * 30
        )
        points_to_archive = queryset.filter(created_at__gte=archive_date)
        points_to_archive.update(is_active=False)

        self.message_user(
            request,
            f"{points_to_archive.count()} точек было перенесено в архив.",
        )

    archive_points.short_description = "Перенести выбранные точки в архив"


@admin.register(ForbiddenZone)
class ForbiddenZoneAdmin(admin.ModelAdmin):
    list_display = ("name",)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


admin.site.register(Equipment)
admin.site.register(Fish)
admin.site.register(FavoritePoint)
admin.site.register(Comment)
admin.site.register(ArchiveSetting)
admin.site.register(PointRating)
admin.site.register(Report)
