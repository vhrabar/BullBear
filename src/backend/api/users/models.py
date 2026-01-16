
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
import random
import string

class User(AbstractUser):
    email = models.EmailField()
    username = models.CharField(unique=True, max_length=150)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

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


class ContactMessage(models.Model):
    """
    Stores submitted contact messages.
    """
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        related_name="contact_messages",
        null=True,
        blank=True,
    )

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.email} - {self.subject}"


class PortfolioSnapshot(models.Model):
    portfolio = models.ForeignKey(UserPortfolio, on_delete=models.CASCADE, related_name="snapshots")
    ts = models.DateTimeField(db_index=True)

    cash_balance = models.DecimalField(max_digits=20, decimal_places=2)
    equity_value = models.DecimalField(max_digits=20, decimal_places=2)
    total_value = models.DecimalField(max_digits=20, decimal_places=2)

    unrealized_pl = models.DecimalField(max_digits=20, decimal_places=2)
    unrealized_pl_pct = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        unique_together = ("portfolio", "ts")
        indexes = [
            models.Index(fields=["portfolio", "ts"]),
        ]



