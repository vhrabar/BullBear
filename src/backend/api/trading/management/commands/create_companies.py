from django.core.management.base import BaseCommand
from django.db import transaction
from api.trading.models import Instrument, Company

class Command(BaseCommand):
    help = "Create Company objects for each Instrument and link them"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        created_count = 0
        linked_count = 0

        # Iterate through all instruments
        for instrument in Instrument.objects.all():
            # Create company if it doesn't exist
            company, created = Company.objects.get_or_create(
                name=instrument.name,
                defaults={'ticker': instrument.symbol}
            )
            if created:
                created_count += 1

            # Link instrument to company if not already linked
            if instrument.company != company:
                instrument.company = company
                instrument.save(update_fields=['company'])
                linked_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} new companies."))
        self.stdout.write(self.style.SUCCESS(f"Linked {linked_count} instruments to companies."))
