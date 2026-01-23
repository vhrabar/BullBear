from rest_framework import serializers
from .models import Fund, FundHolding, FundSubscription, FundNAVHistory, FundComment


class FundCommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = FundComment
        fields = ['id', 'fund', 'user', 'username', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'username', 'created_at', 'updated_at']


class FundHoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundHolding
        fields = ['id', 'instrument', 'weight_percent']
        extra_kwargs = {
            'id': {'read_only': True},
        }


class FundSerializer(serializers.ModelSerializer):
    holdings = FundHoldingSerializer(many=True, required=False)
    owner_username = serializers.SerializerMethodField()
    subscriber_count = serializers.SerializerMethodField()
    total_invested = serializers.SerializerMethodField()

    class Meta:
        model = Fund
        fields = ['id', 'creator_portfolio', 'name', 'description', 'is_active', 'total_units', 'nav_per_unit', 'holdings', 'owner_username', 'subscriber_count', 'total_invested', 'created_at', 'updated_at']
        extra_kwargs = {
            'id': {'read_only': True},
            'is_active': {'required': False},
            'total_units': {'read_only': True},
            'nav_per_unit': {'read_only': True},
        }

    def get_owner_username(self, obj):
        return obj.creator_portfolio.user.user.username

    def get_subscriber_count(self, obj):
        return obj.subscriptions.count()

    def get_total_invested(self, obj):
        from django.db.models import Sum
        total = obj.subscriptions.aggregate(total=Sum('invested_amount'))['total']
        return float(total) if total else 0

    def create(self, validated_data):
        holdings_data = validated_data.pop('holdings', [])
        fund = Fund.objects.create(**validated_data)
        for holding in holdings_data:
            FundHolding.objects.create(fund=fund, **holding)
        return fund

    def update(self, instance, validated_data):
        holdings_data = validated_data.pop('holdings', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update holdings
        instance.holdings.all().delete()
        for holding in holdings_data:
            FundHolding.objects.create(fund=instance, **holding)
        return instance


class FundSubscriptionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='fund.name', read_only=True)
    description = serializers.CharField(source='fund.description', read_only=True)
    nav_per_unit = serializers.DecimalField(source='fund.nav_per_unit', max_digits=20, decimal_places=6, read_only=True)
    fund_id = serializers.IntegerField(source='fund.id', read_only=True)

    class Meta:
        model = FundSubscription
        fields = ['id', 'subscriber_portfolio', 'fund', 'fund_id', 'units', 'invested_amount', 'name', 'description', 'nav_per_unit']


class FundNAVHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FundNAVHistory
        fields = ['id', 'fund', 'nav_per_unit', 'total_units', 'recorded_at']
        read_only_fields = ['id', 'recorded_at']


