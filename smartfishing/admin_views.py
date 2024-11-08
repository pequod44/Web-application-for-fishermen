from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from smartfishing.constants import POINT_TYPES
from smartfishing.models import Point, Report
from users.models import MembershipCard


@method_decorator(staff_member_required, name="dispatch")
class ReportView(TemplateView):
    template_name = "admin/report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["membership_count"] = MembershipCard.objects.count()
        context["point_count"] = Point.objects.count()
        types = []
        for key, name in POINT_TYPES.items():
            count = Point.objects.filter(type=key).count()
            types.append({"name": name, "count": count})
        context["types"] = types
        avg_rating = Point.objects.annotate(
            avg_rating=Avg("ratings__rating"),
        )

        sort_avg_rating = avg_rating.order_by("avg_rating")
        context["highest_rated_point"] = sort_avg_rating.last()
        context["lowest_rated_point"] = sort_avg_rating.first()
        return context


@method_decorator(staff_member_required, name="dispatch")
class ReportListView(TemplateView):
    template_name = "admin/reports_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reports"] = Report.objects.select_related(
            "point", "user"
        ).all()
        return context

    def post(self, request, *args, **kwargs):
        report_id = request.POST.get("report_id")
        Report.objects.filter(id=report_id).delete()
        return redirect("reports_list")
