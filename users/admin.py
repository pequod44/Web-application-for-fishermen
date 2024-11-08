from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import MembershipCard, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "phone",
    )
    list_display_links = ("username",)
    search_fields = (
        "username",
        "email",
        "first_name",
    )
    readonly_fields = ("created_at",)
    empty_value_display = "Не указано"
    fieldsets = (
        (
            "Информация о пользователе",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "patronymic",
                    "username",
                    "date_of_birth",
                    "email",
                    "phone",
                )
            },
        ),
        ("Участник клуба", {"fields": ("membership",)}),
        ("Дата", {"fields": ("created_at",)}),
    )


@admin.register(MembershipCard)
class MembershipCardAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "user",
        "status",
        "expiry_date",
        "is_active",
    )
    search_fields = ("number",)
    list_filter = (
        "status",
        "is_active",
    )
    empty_value_display = "Не указано"
    fields = (
        "number",
        "user",
        "first_name",
        "last_name",
        "patronymic",
        "date_of_birth",
        "phone",
        "status",
        "expiry_date",
        "is_active",
    )
