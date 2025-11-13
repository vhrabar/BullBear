from rest_framework import serializers

from .models import UserPortfolio


class UserPortofolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPortfolio
        fields = '__all__'