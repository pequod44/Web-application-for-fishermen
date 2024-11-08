from datetime import timedelta
from random import randint

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone

from users.constants import (
    EMAIL_LEN,
    FIRST_NAME_LEN,
    LAST_NAME_LEN,
    MEMBERSHIP_NUM_LEN,
    MEMBERSHIP_STATUS,
    PATRONYMIC_LEN,
    PHONE_NUMBER_LEN,
    TICKET_VALIDITY_DURATION_DAY,
    USERNAME_LEN,
)
from users.validators import PhoneNumberRussianFormatValidator


class MembershipCard(models.Model):
    number = models.CharField(
        "Номер членского билета",
        max_length=MEMBERSHIP_NUM_LEN,
        null=True,
        blank=True,
    )
    first_name = models.CharField(
        "Имя",
        max_length=FIRST_NAME_LEN,
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=LAST_NAME_LEN,
    )
    patronymic = models.CharField(
        "Отчество",
        max_length=PATRONYMIC_LEN,
    )
    date_of_birth = models.DateField(
        "Дата рождения",
    )
    expiry_date = models.DateField(
        "Срок действия (до)",
        null=True,
        blank=True,
    )
    phone = models.CharField(
        "Номер телефона",
        max_length=PHONE_NUMBER_LEN,
        blank=True,
        null=True,
        validators=[PhoneNumberRussianFormatValidator()],
    )
    status = models.CharField(
        "Статус",
        choices=tuple(MEMBERSHIP_STATUS.items()),
        default="pending",
    )
    is_active = models.BooleanField(
        "Активный",
        default=True,
    )
    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE,
        related_name="tickets",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("-expiry_date",)
        verbose_name = "FH Club"
        verbose_name_plural = "FH Club"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self.generate_unique_number()
        super().save(*args, **kwargs)

    def generate_unique_number(self):
        while True:
            number = f"{randint(0, 999999):06d}"
            if not MembershipCard.objects.filter(number=number).exists():
                return number

    def mark_as_paid(self, current_user):
        self.status = "paid"
        self.expiry_date = timezone.now() + timedelta(
            days=TICKET_VALIDITY_DURATION_DAY
        )
        self.save()
        self.user = current_user
        self.user.membership = self
        self.user.save()

    def __str__(self):
        return self.number


class User(AbstractUser):
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = (
        "email",
        "first_name",
        "last_name",
        "patronymic",
        "date_of_birth",
    )
    first_name = models.CharField(
        "Имя",
        max_length=FIRST_NAME_LEN,
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=LAST_NAME_LEN,
    )
    patronymic = models.CharField(
        "Отчество",
        max_length=PATRONYMIC_LEN,
    )
    email = models.EmailField(
        "Электронная почта",
        max_length=EMAIL_LEN,
        unique=True,
        validators=[EmailValidator()],
    )
    username = models.CharField(
        "Имя пользователя",
        max_length=USERNAME_LEN,
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )
    phone = models.CharField(
        "Номер телефона",
        max_length=PHONE_NUMBER_LEN,
        null=True,
        blank=True,
        validators=[PhoneNumberRussianFormatValidator()],
    )
    date_of_birth = models.DateField(
        "Дата рождения",
    )
    membership = models.OneToOneField(
        MembershipCard,
        on_delete=models.SET_NULL,
        related_name="owner",
        null=True,
        blank=True,
        verbose_name="Билет клуба",
    )
    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
