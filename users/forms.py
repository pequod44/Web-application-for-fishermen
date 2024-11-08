from django import forms

from users.models import MembershipCard, User


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "patronymic",
            "date_of_birth",
            "phone",
        )


class MembershipCardForm(forms.ModelForm):
    class Meta:
        model = MembershipCard
        fields = ("number",)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)


class MembershipApplicationForm(forms.ModelForm):
    class Meta:
        model = MembershipCard
        fields = (
            "first_name",
            "last_name",
            "patronymic",
            "date_of_birth",
            "phone",
        )
