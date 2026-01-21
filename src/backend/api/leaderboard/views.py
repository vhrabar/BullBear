from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.pagination import PageNumberPagination
from .services import get_leaderboard_queryset

class IsAuthenticatedOrExecutor(BasePermission):
   def has_permission(self, request, view):
      return (request.user and request.user.is_authenticated or getattr(request.user, "is_executor", False))
class LeaderboardView(APIView):
   permission_classes = [IsAuthenticatedOrExecutor]
   def get(self, request):
      time_filter = request.GET.get("time", "all")
      qs = get_leaderboard_queryset(time_filter=time_filter).order_by('-latest_total_value')
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