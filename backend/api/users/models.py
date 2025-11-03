
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True, max_length=150)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def save(self, *args, **kwargs):
        if not self.username and self.email:
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.user.user.username})"

