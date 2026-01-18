from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from .services import get_leaderboard_queryset

class LeaderboardView(APIView):
   permission_classes = [AllowAny]
   def get(self, request):
      qs = get_leaderboard_queryset().order_by('-latest_total_value')
      paginator = PageNumberPagination()
      paginator.page_size = 50
      page = paginator.paginate_queryset(qs, request)
      data = []
      start_rank = (paginator.page.number - 1) * paginator.page_size
      for i, portfolio in enumerate(page, start=1):
         data.append({
            "rank": start_rank + i,
            "username": portfolio.user.user.username,
            "portfolio_name": portfolio.name,
            "total_value": str(portfolio.latest_total_value),
         })
      return paginator.get_paginated_response(data)