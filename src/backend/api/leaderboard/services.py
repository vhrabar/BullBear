from django.db.models import OuterRef, Subquery, DecimalField
from api.users.models import UserPortfolio, PortfolioSnapshot

def get_leaderboard_queryset():
   latest_snapshot = PortfolioSnapshot.objects.filter(portfolio = OuterRef("pk")).order_by("-ts")
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