from api.users.models import UserPortfolio
from rest_framework.exceptions import PermissionDenied


def get_user_portfolio_or_403(user, portfolio_id: int) -> UserPortfolio:
    """
    Returns portfolio if owned by authenticated user, otherwise raises 403.
    """
    try:
        portfolio = UserPortfolio.objects.select_related("user__user").get(id=portfolio_id)
    except UserPortfolio.DoesNotExist:
        raise PermissionDenied("Portfolio not found or access denied.")

    if not hasattr(user, "profile"):
        raise PermissionDenied("Profile missing.")

    if portfolio.user_id != user.profile.id:
        raise PermissionDenied("Portfolio not found or access denied.")

    return portfolio