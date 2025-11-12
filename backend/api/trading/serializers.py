from rest_framework import serializers
from .models import Instrument, InstrumentIntervalData, PortfolioHolding


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
