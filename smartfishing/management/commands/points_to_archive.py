from django.core.management.base import BaseCommand

from smartfishing.models import Point


class Command(BaseCommand):
    help = "Архивировать координаты без комментариев более 90 дней"

    def handle(self, *args, **kwargs):
        Point.objects.to_archive_inactive_points()
        self.stdout.write(self.style.SUCCESS("Точки успешно заархивированы!"))
