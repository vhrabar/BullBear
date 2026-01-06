from django.core.management.base import BaseCommand
from api.trading.models import InstrumentIntervalData


class Command(BaseCommand):
    help = "Delete all instrument interval candles"

    def handle(self, *args, **options):
        count, _ = InstrumentIntervalData.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(
            f"Deleted {count} interval records"
        ))
