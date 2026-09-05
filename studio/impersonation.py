"""Temporary user sessions with a server-side, revocable administrator return ticket."""
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import constant_time_compare
from django.views.decorators.http import require_POST
from .access import administrator

KEY = 'acting_admin'

def original_admin(request):
    ticket = request.session.get(KEY)
    if not isinstance(ticket, dict):
        return None
    admin = User.objects.filter(pk=ticket.get('id'), is_active=True, is_superuser=True).first()
    if admin and constant_time_compare(admin.get_session_auth_hash(), ticket.get('hash', '')):
        return admin
    return None

class ValidateAdministrator:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if KEY in request.session and original_admin(request) is None:
            logout(request)
        return self.get_response(request)

@administrator
@require_POST
def start(request, pk):
    if KEY in request.session:
        raise PermissionDenied('Bitte zuerst zum eigenen Administrator zurückkehren.')
    target = get_object_or_404(User, pk=pk, is_active=True)
    if target.pk == request.user.pk:
        return redirect('manage_users')
    ticket = {'id': request.user.pk, 'hash': request.user.get_session_auth_hash(),
              'browser_session': request.session.get_expire_at_browser_close()}
    login(request, target, backend='django.contrib.auth.backends.ModelBackend')
    request.session[KEY] = ticket
    request.session.set_expiry(0 if ticket['browser_session'] else 365 * 86400)
    return redirect('dashboard')

@require_POST
def stop(request):
    admin = original_admin(request)
    if admin is None:
        raise PermissionDenied('Die Administrator-Sitzung ist nicht mehr gültig. Bitte neu anmelden.')
    browser_session = request.session[KEY]['browser_session']
    logout(request)
    login(request, admin, backend='django.contrib.auth.backends.ModelBackend')
    request.session.set_expiry(0 if browser_session else 365 * 86400)
    return redirect('manage_users')
