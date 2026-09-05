import json
import os
import uuid
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .access import administrator
from deployment.releases import manifest, version

@administrator
def page(request):
    return render(request,'management/updates.html',{'configured':bool(settings.UPDATE_MANIFEST_URL),
        'install_enabled':settings.UPDATE_INSTALL_ENABLED})

@administrator
@require_http_methods(['POST'])
def check(request):
    if not settings.UPDATE_MANIFEST_URL:
        return JsonResponse({'error':'Noch keine Update-Quelle konfiguriert. Trage UPDATE_MANIFEST_URL in der Serverkonfiguration ein.'},status=400)
    try:
        release=manifest(settings.UPDATE_MANIFEST_URL)
        available=version(release['version'])>version(settings.APP_VERSION)
        return JsonResponse({'current':settings.APP_VERSION,'available':available,'release':release,'install_enabled':settings.UPDATE_INSTALL_ENABLED})
    except Exception:
        return JsonResponse({'error':'Die Update-Quelle konnte nicht gelesen werden. Prüfe die konfigurierte HTTPS-Adresse und das Release-Manifest.'},status=502)

@administrator
@require_http_methods(['POST'])
def install(request):
    if not settings.UPDATE_INSTALL_ENABLED or not settings.UPDATE_MANIFEST_URL:
        return JsonResponse({'error':'Button-Updates sind für diese Installation noch nicht eingerichtet. Verwende das LXC-Installationsskript und konfiguriere eine Update-Quelle.'},status=400)
    try:
        requested=json.loads(request.body)
        release=manifest(settings.UPDATE_MANIFEST_URL)
        if requested.get('version')!=release['version'] or version(release['version'])<=version(settings.APP_VERSION):
            return JsonResponse({'error':'Die angebotene Version hat sich geändert. Bitte erneut nach Updates suchen.'},status=409)
        folder=settings.UPDATE_STATE_DIR
        if not folder.is_dir():raise ValueError('Updater nicht installiert')
        if (folder/'active').exists() or (folder/'request.json').exists():
            return JsonResponse({'error':'Ein Update ist bereits vorgemerkt oder läuft.'},status=409)
        job=str(uuid.uuid4())
        request_data={'job':job,'version':release['version'],'sha256':release['sha256']}
        # Publish a complete request atomically; the systemd path unit only sees
        # the final name. Hard-link fails if another administrator won the race.
        temporary=folder/f'.request-{job}'
        with temporary.open('x') as stream:json.dump(request_data,stream)
        try:os.link(temporary,folder/'request.json')
        except FileExistsError:return JsonResponse({'error':'Ein Update wurde bereits gestartet.'},status=409)
        finally:temporary.unlink(missing_ok=True)
        return JsonResponse({'job':job,'version':release['version']},status=202)
    except Exception:
        return JsonResponse({'error':'Update konnte nicht gestartet werden. Prüfe Update-Quelle und den installierten Updater-Dienst.'},status=400)

@administrator
@require_http_methods(['GET'])
def status(request):
    path=settings.UPDATE_STATE_DIR/'status.json'
    try:
        result=json.loads(path.read_text()) if path.exists() else {'state':'idle','progress':0,'message':'Noch kein Update ausgeführt.'}
    except (ValueError,OSError):result={'state':'pending','progress':0,'message':'Update-Status wird vorbereitet …'}
    try:
        queued=json.loads((settings.UPDATE_STATE_DIR/'request.json').read_text())
        if queued.get('job') != result.get('job'):
            result={'state':'pending','job':queued['job'],'progress':0,'message':'Update ist vorgemerkt. Der Dienst startet …'}
    except (OSError,ValueError,KeyError):
        pass
    response=JsonResponse(result);response['Cache-Control']='no-store';return response

@require_http_methods(['GET'])
def health(request):
    from django.db import connection
    try:
        with connection.cursor() as cursor:cursor.execute('SELECT 1')
    except Exception:return JsonResponse({'ok':False},status=503)
    return JsonResponse({'ok':True,'version':settings.APP_VERSION})
