from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
import random
import string

class UserManager(BaseUserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)

    def paid(self):
        return self.get_queryset().paid()

    def regular(self):
        return self.get_queryset().regular()


class UserQuerySet(models.QuerySet):
    def paid(self):
        now = timezone.now()
        return self.filter(
            usersubscription__is_active=True,
            usersubscription__end_date__gte=now,
            usersubscription__package__is_active=True
        ).distinct()

    def regular(self):
        return self.exclude(id__in=self.paid())

class User(AbstractUser):
    email = models.EmailField()
    username = models.CharField(unique=True, max_length=150)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.email:
            self.email = ''.join(random.choices(string.ascii_lowercase, k=10)) + '@example.com'
            
        if not self.username:
            local_part = self.email.split('@')[0]
            base_username = slugify(local_part)
            username_candidate = base_username
            counter = 1
            while User.objects.filter(username=username_candidate).exists():
                username_candidate = f"{base_username}{counter}"
                counter += 1
            self.username = username_candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    @property
    def is_paid_user(self):
        now = timezone.now()
        return self.usersubscription_set.filter(
            is_active=True,
            end_date__gte=now,
            package__is_active=True
        ).exists()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class UserPortfolio(models.Model):
    """Represents one user's investment portfolio."""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="portfolios")
    name = models.CharField(max_length=64)
    balance = models.DecimalField(decimal_places=2, default=10000, max_digits=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.user.user.username})"

