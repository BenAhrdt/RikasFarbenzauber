from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from .models import UserAccess

FIELDS = {'characters':'Figuren', 'rooms':'Räume & Häuser', 'worlds':'Orte & Welten',
          'scenes':'Szenen', 'photos':'Fotos hochladen und Fotobibliothek benutzen', 'delete_projects':'Eigene Projekte und Fotos löschen'}
KINDS = {'character':'characters', 'room':'rooms', 'world':'worlds', 'scene':'scenes', 'drawing':'drawing'}

def capabilities(user):
    if not user.is_authenticated:
        return {key:False for key in FIELDS}
    if user.is_superuser:
        return {**{key:True for key in FIELDS}, 'drawing':True}
    access=UserAccess.objects.filter(user=user).first()
    rights={key:getattr(access,key,True) for key in FIELDS}
    rights['drawing']=any(rights[key] for key in ('characters','rooms','worlds','scenes'))
    return rights

def require(user, capability):
    if not capabilities(user).get(capability,False):
        raise PermissionDenied('Dieser Bereich ist für dein Konto nicht freigegeben.')

def allowed_kinds(user):
    rights=capabilities(user)
    return [kind for kind,key in KINDS.items() if rights[key]]

def administrator(view):
    @login_required
    @wraps(view)
    def wrapped(request,*args,**kwargs):
        if not request.user.is_superuser or request.session.get('acting_admin'):
            raise PermissionDenied('Diese Verwaltung ist nur für Administratoren freigegeben.')
        return view(request,*args,**kwargs)
    return wrapped

def context(request):
    from django.conf import settings
    return {'rights':capabilities(request.user),'app_version':settings.APP_VERSION,'acting_as_user':bool(request.session.get('acting_admin'))}
