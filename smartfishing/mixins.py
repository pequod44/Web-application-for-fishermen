from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import models


class CreatedAndUpdatedDateMixin(models.Model):
    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        abstract = True


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class AuthorOrAdminEditDeleteMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user == self.get_object().user
            or self.request.user.is_superuser
        )
