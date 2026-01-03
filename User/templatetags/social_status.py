from django import template

from allauth.socialaccount.models import SocialAccount

register = template.Library()


@register.simple_tag(takes_context=True)
def has_social_connections(context) -> bool:
    request = context.get("request")
    if not request or not request.user.is_authenticated:
        return False
    return SocialAccount.objects.filter(user=request.user).exists()
