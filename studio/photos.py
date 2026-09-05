"""Private normalized photos. Stored in SQLite so existing backups remain complete."""
import io
import json
import math
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Photo
from .access import require

MAX_BYTES = 12 * 1024 * 1024
MAX_PIXELS = 24_000_000

def normalize(upload, crop):
    if not upload or upload.size > MAX_BYTES:
        raise ValueError('Bitte wähle ein Foto mit höchstens 12 MB.')
    if not isinstance(crop, list) or len(crop) != 4 or any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1 for v in crop):
        raise ValueError('Ungültiger Bildausschnitt.')
    left, top, right, bottom = crop
    if right - left < .05 or bottom - top < .05:
        raise ValueError('Der Bildausschnitt ist zu klein.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(upload, formats=['JPEG', 'PNG', 'WEBP']) as source:
                if source.width * source.height > MAX_PIXELS:
                    raise ValueError('Das Foto ist zu groß. Bitte maximal 24 Megapixel verwenden.')
                source.load()
                image = ImageOps.exif_transpose(source)
                w, h = image.size
                image = image.crop((int(left*w), int(top*h), int(right*w), int(bottom*h)))
                if min(image.size) < 1:
                    raise ValueError('Der Bildausschnitt ist zu klein.')
                image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
                # New RGB canvas strips all original metadata (including GPS).
                rgba = image.convert('RGBA')
                clean = Image.new('RGB', rgba.size, 'white')
                clean.paste(rgba, mask=rgba.getchannel('A'))
                output = io.BytesIO()
                clean.save(output, format='JPEG', quality=85, optimize=True)
                if output.tell() > 1024 * 1024:
                    output = io.BytesIO()
                    clean.save(output, format='JPEG', quality=65, optimize=True)
                if output.tell() > 1024 * 1024:
                    raise ValueError('Das Foto ist zu detailreich. Bitte einen kleineren Ausschnitt wählen.')
                return output.getvalue(), clean.width, clean.height
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        raise ValueError('Bitte ein gültiges JPG-, PNG- oder WebP-Foto wählen. HEIC bitte zuerst als JPG exportieren.') from error

def metadata(photo):
    return {'id': str(photo.id), 'name': photo.name, 'width': photo.width, 'height': photo.height}

@login_required
@require_http_methods(['GET', 'POST'])
def photos(request):
    require(request.user,"photos")
    if request.method == 'GET':
        return JsonResponse({'photos': [metadata(p) for p in Photo.objects.filter(owner=request.user).defer('content')]})
    try:
        name = request.POST.get('name', '').strip()
        if not 1 <= len(name) <= 80:
            raise ValueError('Gib deinem Foto einen Namen (1–80 Zeichen).')
        if Photo.objects.filter(owner=request.user).count() >= 100:
            raise ValueError('Deine Fotobibliothek ist voll (100 Fotos).')
        content, width, height = normalize(request.FILES.get('photo'), json.loads(request.POST.get('crop', '[0,0,1,1]')))
        with transaction.atomic():
            # Serialize uploads per user, including SQLite's database write lock.
            User.objects.filter(pk=request.user.pk).update(last_login=F("last_login"))
            if Photo.objects.filter(owner=request.user).count() >= 100:
                raise ValueError('Deine Fotobibliothek ist voll (100 Fotos).')
            photo = Photo.objects.create(owner=request.user, name=name, width=width, height=height, content=content)
        return JsonResponse(metadata(photo), status=201)
    except (ValueError, TypeError) as error:
        return JsonResponse({'error': str(error)}, status=400)

@login_required
@require_http_methods(['GET'])
def photo_image(request, pk):
    photo = get_object_or_404(Photo, pk=pk, owner=request.user)
    response = HttpResponse(bytes(photo.content), content_type='image/jpeg')
    response['Cache-Control'] = 'private, no-store'
    response['X-Content-Type-Options'] = 'nosniff'
    return response

@login_required
@require_http_methods(['DELETE'])
def delete_photo(request, pk):
    require(request.user,"photos")
    require(request.user,"delete_projects")
    from .models import Project
    with transaction.atomic():
        User.objects.filter(pk=request.user.pk).update(last_login=F('last_login'))
        photo = get_object_or_404(Photo, pk=pk, owner=request.user)
        projects = [p.name for p in Project.objects.filter(owner=request.user).only('name', 'document')
                    if any(o.get('photo', {}).get('id') == str(pk) for o in p.document.get('objects', []))]
        if projects:
            return JsonResponse({'error': 'Dieses Foto wird noch verwendet in: ' + ', '.join(projects[:10]) + (f' und {len(projects)-10} weiteren Projekten' if len(projects)>10 else '') + '. Entferne es dort und speichere die Projekte zuerst.'}, status=409)
        photo.delete()
    return JsonResponse({'ok': True})
