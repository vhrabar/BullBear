from rest_framework import serializers
from django.utils import timezone

from .models import UserPortfolio, UserProfile, ContactMessage, PortfolioSnapshot
from .models import User
from ..payment.models import SubscriptionType, UserSubscription


class UserPortofolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPortfolio
        fields = '__all__'
class SubscriptionTypeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionType
        fields = ["id", "name", "price", "duration_days"]


class UserSubscriptionSerializer(serializers.ModelSerializer):
    package_id = serializers.IntegerField(source="package.id")
    package_price = serializers.DecimalField(source="package.price", max_digits=10, decimal_places=2)
    subscription_type = SubscriptionTypeMiniSerializer(source="package.subscription_type")

    class Meta:
        model = UserSubscription
        fields = [
            "package_id",
            "package_price",
            "subscription_type",
            "start_date",
            "end_date",
            "is_active",
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="user.id")
    username = serializers.CharField(source="user.username")
    first_name = serializers.CharField(source="user.first_name", allow_blank=True)
    last_name = serializers.CharField(source="user.last_name", allow_blank=True)
    bio = serializers.CharField(allow_blank=True)
    avatar_url = serializers.CharField(allow_blank=True)
    subscription = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "bio",
            "avatar_url",
            "subscription",
        ]

    def get_subscription(self, obj):
        now = timezone.now()

        sub = (
            UserSubscription.objects
            .filter(
                user=obj.user,
                is_active=True,
                end_date__gte=now,
                package__is_active=True,
            )
            .select_related("package__subscription_type")
            .order_by("-end_date")
            .first()
        )

        if not sub:
            return None

        return UserSubscriptionSerializer(sub).data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")
        extra_kwargs = {"username": {"required": False}}


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    # allow updating a few user fields alongside profile
    username = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = UserProfile
        fields = ("id", "user", "bio", "avatar_url", "username", "first_name", "last_name")
        read_only_fields = ("user",)

    def update(self, instance, validated_data):
        # pop user-related fields
        username = validated_data.pop("username", None)
        first_name = validated_data.pop("first_name", None)
        last_name = validated_data.pop("last_name", None)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        user = instance.user
        if username:
            if User.objects.exclude(pk=user.pk).filter(username=username).exists():
                raise serializers.ValidationError({"username": "This username is already taken."})
            user.username = username
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name

        user.save()

        return instance

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
