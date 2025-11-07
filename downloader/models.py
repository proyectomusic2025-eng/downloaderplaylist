from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
class Plan(models.Model):
    name = models.CharField(max_length=80)
    max_downloads = models.IntegerField(default=5)
    price_cents = models.IntegerField(default=0)
    stripe_price_id = models.CharField(max_length=200, blank=True, null=True)
    show_ads = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} ({self.max_downloads} desc.)"
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    downloads_used = models.IntegerField(default=0)
    def remaining_downloads(self):
        if not self.plan:
            return 0
        return max(0, self.plan.max_downloads - self.downloads_used)
    def __str__(self):
        return f"Profile: {self.user.username}"
class DownloadRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    created_at = models.DateTimeField(default=timezone.now)
    source_url = models.URLField()
    def __str__(self):
        return f"{self.title} - {self.user.username}"
class LicenseKey(models.Model):
    key = models.CharField(max_length=64, unique=True)
    owner_email = models.EmailField(null=True, blank=True)
    plan_name = models.CharField(max_length=100, default='basic')
    max_devices = models.IntegerField(default=1)
    expires_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    def __str__(self):
        return f"{self.key} ({self.plan_name})"
class Activation(models.Model):
    license = models.ForeignKey(LicenseKey, on_delete=models.CASCADE)
    hwid = models.CharField(max_length=200)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    revoked = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.license.key} on {self.hwid}"
