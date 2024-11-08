from rest_framework.permissions import BasePermission


class IsTouristPoint(BasePermission):
    """Для проверки типа точки.

    Может ли пользователь добавлять, редактировать
    и удалять точки типа "Туристическая база".
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if request.method == "POST" and view.action == "create":
            if request.data.get("type") == "camping":
                return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if view.action in ["update", "partial_update", "destroy"]:
            if obj.type == "camping":
                return False
        return True
