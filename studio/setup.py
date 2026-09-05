from django.contrib.auth.models import User
from .models import Installation


def setup_required():
    if Installation.objects.filter(pk=1, completed=True).exists():
        return False
    if User.objects.filter(is_superuser=True).exists():
        Installation.objects.filter(pk=1).update(completed=True)
        return False
    return True
