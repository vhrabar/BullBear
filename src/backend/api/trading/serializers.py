from rest_framework import serializers
from .models import Instrument, InstrumentIntervalData, PortfolioHolding, InstrumentQuote, Company, CompanyNews, \
    EarningsReport, Dividend


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = '__all__'


class InstrumentIntervalDataSerializer(serializers.ModelSerializer):
    instrument = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = InstrumentIntervalData
        fields = '__all__'


class LatestInstrumentDataSerializer(serializers.ModelSerializer):
    instrument = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = InstrumentIntervalData
        fields = '__all__'


class PortfolioHoldingSerializer(serializers.ModelSerializer):
    instrument = serializers.StringRelatedField(read_only=True)
    current_value = serializers.DecimalField(max_digits=20, decimal_places=6, read_only=True)
    profit_loss = serializers.DecimalField(max_digits=20, decimal_places=6, read_only=True)

    class Meta:
        model = PortfolioHolding
        fields = '__all__'

class BuySellSerializer(serializers.Serializer):
    instrument_symbol = serializers.CharField(max_length=16)
    quantity = serializers.DecimalField(max_digits=20, decimal_places=4)
    price = serializers.DecimalField(max_digits=20, decimal_places=6, required=False)



class InstrumentQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentQuote
        fields = [
            "instrument",
            "bid_price",
            "bid_size",
            "ask_price",
            "ask_size",
            "last_price",
            "currency",
            "exchange",
            "market_state",
            "daily_change",
            "daily_change_percent",
            "timestamp",
        ]


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'ticker', 'sector', 'industry', 'description', 'website', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CompanyNewsSerializer(serializers.ModelSerializer):
    companies = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), many=True)

    class Meta:
        model = CompanyNews
        fields = ['id', 'companies', 'headline', 'content', 'published_at', 'source', 'url', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class EarningsReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EarningsReport
        fields = "__all__"

class DividendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dividend
        fields = "__all__"