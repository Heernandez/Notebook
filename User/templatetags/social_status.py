from django import template

from allauth.socialaccount.models import SocialAccount

register = template.Library()


@register.simple_tag(takes_context=True)
def has_social_connections(context) -> bool:
    request = context.get("request")
    if not request or not request.user.is_authenticated:
        return False
    return SocialAccount.objects.filter(user=request.user).exists()


@register.simple_tag
def user_avatar_url(user) -> str:
    if not user or not getattr(user, "is_authenticated", False):
        return ""
    if hasattr(user, "socialaccount_set"):
        accounts = user.socialaccount_set.all()
    else:
        accounts = SocialAccount.objects.filter(user=user)
    account = accounts.first()
    if not account:
        return ""
    return account.get_avatar_url() or ""
