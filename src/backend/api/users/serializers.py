from rest_framework import serializers

from .models import UserPortfolio, UserProfile, User


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