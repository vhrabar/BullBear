from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import OuterRef, Subquery, DecimalField
from api.users.models import UserPortfolio, PortfolioSnapshot

def get_leaderboard_queryset(time_filter = "all"):
   now = timezone.now()
   if time_filter == "1Y":
      cutoff = now - relativedelta(years=1)
   elif time_filter == "1W":
      cutoff = now - timedelta(days=7)
   elif time_filter == "1D":
      cutoff = now - timedelta(days=1)
   elif time_filter == "1M":
      cutoff = now - relativedelta(months=1)
   elif time_filter == "3M":
      cutoff = now - relativedelta(months=3)
   else:
      cutoff = None
   snapshots = PortfolioSnapshot.objects.filter(portfolio = OuterRef('pk'))
   if cutoff:
      snapshots = snapshots.filter(ts__gte = cutoff)
   latest_snapshot = snapshots.order_by("-ts")
   return(
      UserPortfolio.objects.filter(is_active = True).annotate(
         latest_total_value = Subquery(
         latest_snapshot.values("total_value")[:1],
         output_field=DecimalField(),
      ),
      latest_ts = Subquery(
         latest_snapshot.values("ts")[:1],
      ),
      ).exclude(latest_total_value__isnull = True).select_related("user__user").order_by("-latest_total_value")
   )