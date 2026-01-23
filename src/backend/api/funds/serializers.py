from rest_framework import serializers
from .models import Fund, FundHolding, FundSubscription


class FundHoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundHolding
        fields = ['id', 'instrument', 'weight_percent']
        extra_kwargs = {
            'id': {'read_only': True},
        }


class FundSerializer(serializers.ModelSerializer):
    holdings = FundHoldingSerializer(many=True, required=False)

    class Meta:
        model = Fund
        fields = ['id', 'creator_portfolio', 'name', 'description', 'is_active', 'total_units', 'nav_per_unit', 'holdings']
        extra_kwargs = {
            'id': {'read_only': True},
            'is_active': {'required': False},
            'total_units': {'read_only': True},
            'nav_per_unit': {'read_only': True},
        }

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
    class Meta:
        model = FundSubscription
        fields = ['id', 'subscriber_portfolio', 'fund', 'units', 'invested_amount']

