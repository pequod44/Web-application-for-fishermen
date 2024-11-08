from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from smartfishing.constants import POINT_TYPES
from smartfishing.forms import (
    CommentForm,
    ForbiddenZoneForm,
    PointForm,
    RatingForm,
    RegisterForm,
    ReportForm,
)
from smartfishing.mixins import (
    AdminRequiredMixin,
    AuthorOrAdminEditDeleteMixin,
)
from smartfishing.models import (
    Comment,
    FavoritePoint,
    ForbiddenZone,
    Point,
    PointRating,
)


class HomePageView(TemplateView):
    template_name = "smartfishing/home.html"


class MapPageView(TemplateView):
    template_name = "smartfishing/map.html"


class SignUpView(FormView):
    template_name = "registration/sign_up.html"
    form_class = RegisterForm
    success_url = "/"

    def form_valid(self, form):
        login(self.request, form.save())
        return super().form_valid(form)


class PointDetailView(View):
    def get(self, request, point_id):
        point = get_object_or_404(Point, pk=point_id)
        comments = point.comments.all()
        comment_form = CommentForm()
        report_form = ReportForm()
        rating_form = RatingForm()
        is_favorite = (
            FavoritePoint.objects.filter(
                user=request.user, point=point
            ).exists()
            if request.user.is_authenticated
            else False
        )
        avg_rating = point.ratings.aggregate(avg_rating=Avg("rating"))

        return render(
            request,
            "points/detail.html",
            {
                "point": point,
                "is_favorite": is_favorite,
                "comments": comments,
                "comment_form": comment_form,
                "report_form": report_form,
                "rating_form": rating_form,
                "avg_rating": round(avg_rating.get("avg_rating", 0) or 0, 2),
            },
        )

    def post(self, request, point_id):
        point = get_object_or_404(Point, pk=point_id)

        rating_form = RatingForm(request.POST)
        if rating_form.is_valid():
            PointRating.objects.update_or_create(
                user=request.user,
                point=point,
                defaults={"rating": rating_form.cleaned_data["rating"]},
            )
            point.save()
            messages.success(request, "Рейтинг был обновлен")
            return redirect("point_detail", point_id=point.id)

        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            report = report_form.save(commit=False)
            report.user = request.user
            report.point = point
            report.save()
            messages.success(request, "Ваша жалоба была отправлена")
            return redirect("point_detail", point_id=point.id)

        comments = point.comments.all()
        comment_form = CommentForm()
        is_favorite = (
            FavoritePoint.objects.filter(
                user=request.user, point=point
            ).exists()
            if request.user.is_authenticated
            else False
        )

        # rating_form = RatingForm(initial={"rating": point.rating})
        avg_rating = point.ratings.aggregate(avg_rating=Avg("rating"))

        return render(
            request,
            "points/detail.html",
            {
                "point": point,
                "is_favorite": is_favorite,
                "comments": comments,
                "comment_form": comment_form,
                "report_form": report_form,
                "rating_form": rating_form,
                "avg_rating": round(avg_rating.get("avg_rating", 0) or 0, 2),
            },
        )


class PointTypeView(TemplateView):
    template_name = "points/by_type.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        point_type = kwargs.get("point_type")
        context["points"] = Point.objects.filter(type=point_type)
        context["point_type"] = POINT_TYPES.get(point_type, point_type)
        return context


class EditPointView(
    LoginRequiredMixin, AuthorOrAdminEditDeleteMixin, UpdateView
):
    model = Point
    form_class = PointForm
    template_name = "points/edit.html"
    context_object_name = "point"
    pk_url_kwarg = "point_id"
    success_url = reverse_lazy("point_detail")
    success_message = "Точка успешно обновлена."

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка при обновлении точки.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy(
            "point_detail", kwargs={"point_id": self.object.pk}
        )


class DeletePointView(
    LoginRequiredMixin, AuthorOrAdminEditDeleteMixin, DeleteView
):
    model = Point
    pk_url_kwarg = "point_id"
    success_message = "Точка успешно удалена."
    success_url = reverse_lazy("show_map")


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, point_id):
        point = get_object_or_404(Point, id=point_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.point = point
            comment.save()
            messages.success(request, "Комментарий добавлен.")
        else:
            messages.error(request, "Ошибка при добавлении комментария.")

        return redirect("point_detail", point_id=point_id)


class EditCommentView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "comments/edit.html"
    pk_url_kwarg = "comment_id"
    success_message = "Комментарий успешно отредактирован."

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка при редактировании комментария.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy(
            "point_detail", kwargs={"point_id": self.object.point.id}
        )


class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = "comment_id"
    success_message = "Комментарий удалён."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            "point_detail", kwargs={"point_id": self.object.point.id}
        )


class AddToFavoriteView(LoginRequiredMixin, View):
    def post(self, request, point_id):
        point = get_object_or_404(Point, id=point_id)
        favorite = FavoritePoint.objects.filter(user=request.user, point=point)
        if favorite.exists():
            favorite.delete()
            messages.success(request, "Локация удалена из избранного.")
        else:
            FavoritePoint.objects.create(user=request.user, point=point)
            messages.success(request, "Локация добавлена в избранное.")
        return redirect("point_detail", point_id=point_id)


class FavoritePointListView(LoginRequiredMixin, ListView):
    model = FavoritePoint
    template_name = "points/favorites.html"
    context_object_name = "favorites"

    def get_queryset(self):
        return FavoritePoint.objects.filter(user=self.request.user)


class ForbiddenZoneCreateView(
    LoginRequiredMixin, AdminRequiredMixin, CreateView
):
    model = ForbiddenZone
    form_class = ForbiddenZoneForm
    template_name = "forbidden_zones/form.html"
    success_url = reverse_lazy("forbidden_zone_list")


class ForbiddenZoneUpdateView(
    LoginRequiredMixin, AdminRequiredMixin, UpdateView
):
    model = ForbiddenZone
    form_class = ForbiddenZoneForm
    template_name = "forbidden_zones/form.html"
    success_url = reverse_lazy("forbidden_zone_list")


class ForbiddenZoneListView(LoginRequiredMixin, ListView):
    model = ForbiddenZone
    template_name = "forbidden_zones/list.html"
    context_object_name = "forbidden_zones"


class ArchivePointsView(LoginRequiredMixin, ListView):
    template_name = "points/archives.html"
    context_object_name = "archives"

    def get_queryset(self):
        return Point.objects.filter(user=self.request.user, is_active=False)
