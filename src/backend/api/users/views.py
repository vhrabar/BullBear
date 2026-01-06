import pandas as pd
from rest_framework import viewsets, request
from .models import UserPortfolio, UserProfile
from api.trading.models import Transaction, Instrument
from .serializers import UserPortofolioSerializer, UserProfileSerializer
from rest_framework import permissions
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_datetime


class UserPortfolioViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserPortofolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile = self.request.user.profile
        return UserPortfolio.objects.filter(user=profile)

@require_POST
def import_csv(request):
    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "No file uploaded"}, status = 400)
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    records = df.to_dict(orient = "records")
    required_fields = {"email", "portfolio_name", "instrument_symbol", "type", "quantity", "price"}
    for i, row in enumerate(records):
        for field in required_fields:
            if field not in row or pd.isna(row[field]) or row[field] == "":
                return JsonResponse(
                    {"error": f"Missing value for '{field}' in row {i+1}"},
                    status = 400
                    )
    for row in records:
        user, _ = User.objects.get_or_create(
            email = row["email"],
            defaults = {"username": row.get("username") or ""}
        )
        profile, _ = UserProfile.objects.get_or_create(user = user)
        portfolio, _ = UserPortfolio.objects.get_or_create(
            user = profile,
            name = row["portfolio_name"],
            defaults = {"balance": 10000}
        )
        instrument, _ = Instrument.objects.get_or_create(
            symbol = row["instrument_symbol"],
            defaults = {"name": row.get("instrument_name") or row["instrument_symbol"], "type": "STOCK"}
        )
        executed_at_str = row.get("executed_at")
        executed_at = parse_datetime(str(executed_at_str)) if executed_at_str else None
        Transaction.objects.create(
            portfolio = portfolio,
            instrument = instrument,
            type = row["type"].lower(),
            quantity = float(row["quantity"]),
            price = float(row["price"]),
            executed_at = executed_at
        )
    return JsonResponse({"records": records})

def export_csv(request):
    transactions = Transaction.objects.select_related(
        "portfolio__user__user", "instrument"
    ).all()

    data = []
    for t in transactions:
        data.append({
            "email": t.portfolio.user.user.email,
            "username": t.portfolio.user.user.username,
            "portfolio_name": t.portfolio.name,
            "instrument_symbol": t.instrument.symbol,
            "instrument_name": t.instrument.name,
            "type": t.type,
            "quantity": float(t.quantity),
            "price": float(t.price),
            "executed_at": t.executed_at.strftime("%Y-%m-%d %H:%M:%S") if t.executed_at else "",
        })

    df = pd.DataFrame(data)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="transactions.csv"'
    df.to_csv(response, index=False)
    return response

class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)