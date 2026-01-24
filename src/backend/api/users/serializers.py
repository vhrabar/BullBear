from rest_framework import serializers

from .models import UserPortfolio, UserProfile, ContactMessage, PortfolioSnapshot


class UserPortofolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPortfolio
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_paid_user",
        ]
        read_only_fields = [
            "id",
            "is_paid_user",
        ]

class ContactDefaultsSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ("full_name", "email", "subject", "message")

    def validate_full_name(self, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Full name is too short.")
        return value

    def validate_subject(self, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Subject is too short.")
        return value

    def validate_message(self, value: str) -> str:
        value = value.strip()
        if len(value) < 1:
            raise serializers.ValidationError("Message is too short.")
        return value


class PortfolioSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioSnapshot
        fields = (
            "portfolio",
            "ts",
            "cash_balance",
            "equity_value",
            "total_value",
            "unrealized_pl",
            "unrealized_pl_pct",
            "realized_pl",
            "realized_pl_pct",
        )
        read_only_fields = ("id",)
