from django import template
register = template.Library()


from django.conf import settings
from account.models import Profile
# User = settings.AUTH_USER_MODEL


@register.filter
def not_self(users, key):
    return users.exclude(pk = key)

