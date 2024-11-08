from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from users.forms import (
    MembershipApplicationForm,
    MembershipCardForm,
    UserProfileForm,
)
from users.models import MembershipCard


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user"] = user
        context["membership"] = MembershipCard.objects.filter(
            user=user
        ).first()
        context["points"] = user.points.all()
        return context


class ProfileEditView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile_edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user_form"] = UserProfileForm(instance=user)
        context["membership_form"] = MembershipCardForm(
            instance=user.membership,
            user=user,
        )
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        user_form = UserProfileForm(request.POST, instance=user)
        membership_form = MembershipCardForm(
            request.POST,
            instance=user.membership,
            user=user,
        )
        context = self.get_context_data(
            user_form=user_form,
            membership_form=membership_form,
        )

        if user_form.is_valid() and membership_form.is_valid():
            number = membership_form.cleaned_data.get("number")
            phone = user_form.cleaned_data.get("phone")

            if number and not phone:
                context["error"] = (
                    "Номер телефона обязателен, "
                    "если указан номер членского билета"
                )
                return self.render_to_response(context)

            user_form.save()
            if number:
                try:
                    card = MembershipCard.objects.get(number=number)
                    compare = [
                        card.first_name == user.first_name,
                        card.last_name == user.last_name,
                        card.patronymic == user.patronymic,
                        card.date_of_birth == user.date_of_birth,
                    ]

                    if all(compare):
                        card.user = user
                        user.membership = card
                        card.save()
                        user.save()
                    else:
                        context["error"] = (
                            "Ошибка в введенных данных или "
                            "такого членского билета не существует"
                        )
                        return self.render_to_response(context)
                except MembershipCard.DoesNotExist:
                    context["error"] = (
                        "Членский билет " f"№{number} не существует"
                    )
                    return self.render_to_response(context)

            return redirect("profile")
        return self.render_to_response(context)


class MembershipApplicationView(LoginRequiredMixin, TemplateView):
    template_name = "memberships/send.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["membership_form"] = MembershipApplicationForm()
        return context

    def post(self, request, *args, **kwargs):
        membership_form = MembershipApplicationForm(request.POST)

        card = MembershipCard.objects.filter(user=self.request.user).first()
        if card:
            context = self.get_context_data(membership_form=membership_form)
            context["error"] = (
                f"Вы уже отправили заявку. Ваш билет №{card.number}"
            )
            return self.render_to_response(context)

        if membership_form.is_valid():
            membership_card = membership_form.save(commit=False)
            membership_card.user = request.user
            membership_card.status = "pending"
            membership_card.save()
            return redirect("membership_status")

        context = self.get_context_data()
        context["membership_form"] = membership_form
        return self.render_to_response(context)


class MembershipVerifyView(LoginRequiredMixin, TemplateView):
    template_name = "memberships/payment.html"

    def get_context_data(self, **kwargs):
        membership_id = self.kwargs.get("membership_id")
        membership = MembershipCard.objects.filter(pk=membership_id).first()
        context = super().get_context_data(**kwargs)

        if not membership:
            context["error"] = "Билет не существует"
            return context

        if membership.user != self.request.user:
            context["error"] = "Доступ заперещен"
            return context

        membership.mark_as_paid(self.request.user)
        context["membership"] = membership
        return context


class MembershipStatusView(LoginRequiredMixin, TemplateView):
    template_name = "memberships/status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["membership"] = MembershipCard.objects.filter(
            user=self.request.user
        ).first()
        return context

    def post(self, request, *args, **kwargs):
        membership_id = request.POST.get("membership_id")
        action = request.POST.get("action")
        membership = MembershipCard.objects.get(id=membership_id)

        if action == "approved":
            membership.status = "paid"
            membership.mark_as_paid(self.request.user)
            membership.save()

        return redirect("profile")


class MembershipPaymentView(LoginRequiredMixin, View):
    def get(self, request, membership_id):
        membership = get_object_or_404(MembershipCard, pk=membership_id)
        return render(
            request,
            "memberships/payment_form.html",
            {"membership": membership},
        )

    def post(self, request, membership_id):
        membership = get_object_or_404(MembershipCard, pk=membership_id)
        membership.mark_as_paid(request.user)
        return redirect(reverse("profile"))
