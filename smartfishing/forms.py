from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.gis import forms as gis_forms

from smartfishing.constants import RATING
from smartfishing.models import Comment, ForbiddenZone, Point, Report
from users.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "patronymic",
            "date_of_birth",
            "phone",
        )


class PointForm(gis_forms.ModelForm):
    class Meta:
        model = Point
        fields = (
            "name",
            "description",
            "image",
            "type",
            "coordinates",
        )
        widgets = {
            "coordinates": gis_forms.OSMWidget(
                attrs={
                    "map_width": "800",
                    "map_height": "600",
                    "map_srid": 4326,
                    "default_lat": 46.347141,
                    "default_lon": 48.026459,
                    "default_zoom": 20,
                }
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("message",)


class ForbiddenZoneForm(forms.ModelForm):
    class Meta:
        model = ForbiddenZone
        fields = ("name", "boundary")


class PaymentForm(forms.Form):
    card_number = forms.CharField(
        label="Номер карты",
        max_length=16,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    expiry_date = forms.CharField(
        label="Срок действия",
        max_length=5,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "MM/YY"}
        ),
    )
    cvc = forms.CharField(
        label="CVC",
        max_length=3,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    cardholder_name = forms.CharField(
        label="Имя владельца",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["type", "description"]
        widgets = {
            "type": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 5}
            ),
        }
        labels = {
            "type": "Тип жалобы",
            "description": "Описание жалобы",
        }


class RatingForm(forms.Form):
    rating = forms.ChoiceField(
        label="Рейтинг",
        choices=tuple(RATING.items()),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
