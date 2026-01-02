from django.conf import settings
from django.db import models
from django.utils import timezone


class UserOTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otps",
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at
