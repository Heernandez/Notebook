from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        full_name = (data.get("name") or "").strip()
        if settings.DEBUG:
            print(
                "SocialAccountAdapter.populate_user data:",
                {k: data.get(k) for k in ("name", "first_name", "last_name", "email")},
            )
            print(
                "SocialAccountAdapter.populate_user extra_data:",
                sociallogin.account.extra_data,
            )
        if full_name:
            user.first_name = full_name

        email = (data.get("email") or "").strip().lower()
        if not email:
            email = (sociallogin.account.extra_data.get("email") or "").strip().lower()
        if email:
            user.email = email
            user.username = email
        else:
            base_username = slugify(full_name) or "user"
            User = get_user_model()
            candidate = base_username[:150]
            suffix = 1
            while User.objects.filter(username=candidate).exists():
                suffix += 1
                candidate = f"{base_username[:140]}{suffix}"
            user.username = candidate
        return user
