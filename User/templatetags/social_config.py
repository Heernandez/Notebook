from django import template
from django.contrib.sites.shortcuts import get_current_site

from allauth.socialaccount.models import SocialApp

register = template.Library()


@register.simple_tag(takes_context=True)
def social_app_configured(context, provider: str) -> bool:
    request = context.get("request")
    if not request:
        return False
    site = get_current_site(request)
    return SocialApp.objects.filter(provider=provider, sites=site).exists()
