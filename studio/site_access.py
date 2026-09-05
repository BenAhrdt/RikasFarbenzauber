import ipaddress
import socket
from urllib.parse import urlsplit
from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from .access import administrator
from .models import SiteAccess


from deployment.access_config import origin


def origins():
    stored=SiteAccess.objects.filter(pk=1).first()
    return stored.https_origins if stored else settings.RIKA_HTTPS_ORIGINS


class AccessForm(forms.Form):
    addresses=forms.CharField(label='Freigegebene HTTPS-Adressen',required=False,widget=forms.Textarea(attrs={'rows':5}),help_text='Eine Adresse pro Zeile. Leer lassen, um nur lokalen Zugriff zu erlauben.')
    def clean_addresses(self):
        try:
            values=list(dict.fromkeys(origin(line) for line in self.cleaned_data['addresses'].splitlines() if line.strip()))
            if len(values)>20:raise ValueError('Höchstens 20 Adressen sind möglich.')
            return values
        except ValueError as exc:raise forms.ValidationError(str(exc))


@administrator
def configure(request):
    form=AccessForm(request.POST if request.method=='POST' else None,initial={'addresses':'\n'.join(origins())})
    if request.method=='POST' and form.is_valid():
        SiteAccess.objects.update_or_create(pk=1,defaults={'https_origins':form.cleaned_data['addresses']})
        messages.success(request,'HTTPS-Adressen gespeichert. Der lokale Zugang bleibt erreichbar.')
        return redirect('manage_access')
    return render(request,'management/access.html',{'form':form,'local_access':settings.RIKA_LOCAL_ACCESS})


def local_hosts():
    hosts={'localhost','127.0.0.1','::1',socket.gethostname().lower()}
    # Discover actual interface addresses; never allow arbitrary private Host headers.
    import fcntl,struct
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        for _,name in socket.if_nameindex():
            try:hosts.add(socket.inet_ntoa(fcntl.ioctl(sock.fileno(),0x8915,struct.pack('256s',name.encode()[:15]))[20:24]))
            except OSError:pass
    try:
        from pathlib import Path
        for line in Path('/proc/net/if_inet6').read_text().splitlines():
            hosts.add(str(ipaddress.IPv6Address(int(line.split()[0],16))))
    except OSError:pass
    return hosts


class LocalAndHttps:
    """Host allowlist, local HTTP and separate secure HTTPS cookies, per request."""
    def __init__(self,get_response):self.get_response=get_response
    def __call__(self,request):
        if not settings.RIKA_LOCAL_ACCESS:return self.get_response(request)
        try:
            host=request.get_host()
            parsed=urlsplit('//'+host)
            hostname=parsed.hostname or ''
            port=parsed.port
            authority=hostname.lower()+(f':{port}' if port and port!=443 else '')
            local=hostname.lower() in local_hosts()
            secure=request.is_secure()
            if not local and ('https://'+authority not in origins() or not secure):
                return HttpResponseForbidden('Diese Adresse ist nicht freigegeben. Bitte den lokalen Zugang oder eine freigegebene HTTPS-Adresse verwenden.')
        except ValueError:return HttpResponseForbidden('Ungültige Adresse.')
        names=(settings.SESSION_COOKIE_NAME,settings.CSRF_COOKIE_NAME)
        if secure:
            for name in names:
                request.COOKIES.pop(name,None)
                if '__Host-'+name in request.COOKIES:request.COOKIES[name]=request.COOKIES['__Host-'+name]
        response=self.get_response(request)
        if secure:
            for name in names:
                if name in response.cookies:
                    cookie=response.cookies.pop(name)
                    response.cookies['__Host-'+name]=cookie.value
                    for key,value in cookie.items():response.cookies['__Host-'+name][key]=value
                    response.cookies['__Host-'+name]['secure']=True
                    response.cookies['__Host-'+name]['path']='/'
                    response.cookies['__Host-'+name]['domain']=''
        return response
