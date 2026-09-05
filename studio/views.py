import hashlib, json
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import Project, LoginAttempt, Installation, Photo
from .forms import SetupForm
from .setup import setup_required
from django.contrib.auth.models import User
from .schema import validate_document
from .access import require, allowed_kinds, KINDS
@require_http_methods(["GET", "POST"])
def login_view(request):
    if setup_required():
        return redirect("setup")
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = AuthenticationForm(request, data=request.POST or None)
    limited = False
    if request.method == "POST":
        address = request.META.get("HTTP_X_REAL_IP", request.META.get("REMOTE_ADDR", "unknown")) if not settings.DEBUG else request.META.get("REMOTE_ADDR", "unknown")
        key = hashlib.sha256(address.encode()).hexdigest()
        with transaction.atomic():
            attempt, _ = LoginAttempt.objects.get_or_create(key=key, defaults={"started_at": timezone.now()})
            if attempt.started_at < timezone.now() - timedelta(minutes=15):
                attempt.count, attempt.started_at = 0, timezone.now()
            limited = attempt.count >= 10
            if not limited:
                attempt.count += 1
            attempt.save()
        if not limited and form.is_valid():
            login(request, form.get_user())
            request.session.set_expiry(settings.SESSION_COOKIE_AGE if request.POST.get("remember") else 0)
            LoginAttempt.objects.filter(key=key).delete()
            return redirect("dashboard")
    return render(request, "registration/login.html", {"form": form, "limited": limited}, status=429 if limited else 200)
@login_required
def dashboard(request):
    kind = request.GET.get("kind", "character")
    if kind not in ("character", "room", "world", "scene"):
        kind = "character"
    allowed = allowed_kinds(request.user)
    if kind not in allowed:
        kind = allowed[0] if allowed else "character"
    labels = {"character": "Figur", "room": "Raum oder Haus", "world": "Ort", "scene": "Szene"}
    return render(request, "dashboard.html", {"projects": Project.objects.filter(owner=request.user, kind=kind, kind__in=allowed), "kind": kind, "kind_label": labels[kind]})
@login_required
def editor(request, pk=None):
    project = get_object_or_404(Project, pk=pk, owner=request.user) if pk else None
    kind = project.kind if project else request.GET.get("kind", "character")
    if kind not in ("character", "room", "world", "scene"):
        kind = "character"
    require(request.user, KINDS[kind])
    return render(request, "editor.html" if kind == "character" else "space.html", {"project_data": serialize(project) if project else None, "kind": kind})
def serialize(p):
    return {"id": str(p.id), "name": p.name, "kind": p.kind, "document": p.document, "revision": p.revision, "updated_at": p.updated_at.isoformat()}
def payload(request, kind=None):
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict) or not isinstance(data.get("name"), str) or not 1 <= len(data["name"].strip()) <= 80:
            raise ValueError("Bitte gib einen Namen mit 1 bis 80 Zeichen ein.")
        kind = kind or data.get("kind", "character")
        if kind not in ("character", "room", "world", "scene"):
            raise ValueError("Unbekannter Projekttyp.")
        validate_document(data.get("document"))
        if data["document"]["version"] != (1 if kind == "character" else 2):
            raise ValueError("Dokument passt nicht zum Projekttyp.")
        photo_objects = [o for o in data["document"]["objects"] if o["asset"] == "photo-v1"]
        owned = {str(p.id): p for p in Photo.objects.filter(owner=request.user, id__in=[o["photo"]["id"] for o in photo_objects]).defer('content')}
        for obj in photo_objects:
            ref = obj['photo']
            photo = owned.get(ref['id'])
            if photo is None or (ref['width'], ref['height']) != (photo.width, photo.height):
                raise ValueError('Foto nicht verfügbar.')
        data["kind"] = kind
        return data
    except (ValueError, TypeError, KeyError):
        raise ValueError("Das Projekt ist ungültig. Bitte prüfe Name und Figur.")
@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def projects(request):
    if request.method == "GET":
        return JsonResponse({"projects": [serialize(p) for p in Project.objects.filter(owner=request.user, kind__in=allowed_kinds(request.user))]})
    User.objects.filter(pk=request.user.pk).update(last_login=F("last_login"))
    try:
        data = payload(request)
    except ValueError as error:
        return JsonResponse({"error": str(error)}, status=400)
    require(request.user, KINDS[data["kind"]])
    p = Project.objects.create(owner=request.user, name=data["name"].strip(), document=data["document"], kind=data["kind"])
    return JsonResponse(serialize(p), status=201)
@login_required
@require_http_methods(["GET", "PUT", "DELETE"])
def project(request, pk):
    with transaction.atomic():
        if request.method != "GET":
            User.objects.filter(pk=request.user.pk).update(last_login=F("last_login"))
        p = get_object_or_404(Project, pk=pk, owner=request.user)
        require(request.user, KINDS[p.kind])
        if request.method == "DELETE":
            require(request.user, "delete_projects")
            p.delete()
            return JsonResponse({"ok": True})
        if request.method == "PUT":
            try:
                data = payload(request, p.kind)
            except ValueError as error:
                return JsonResponse({"error": str(error)}, status=400)
            if data.get("revision") != p.revision:
                return JsonResponse({"error": "Diese Figur wurde auf einem anderen Gerät geändert. Öffne sie erneut; deine Änderungen kannst du vorher als PNG sichern."}, status=409)
            p.name, p.document = data["name"].strip(), data["document"]
            p.revision += 1
            p.save()
        return JsonResponse(serialize(p))


@require_http_methods(["GET", "POST"])
def setup_view(request):
    if not setup_required():
        return HttpResponseForbidden("Die Ersteinrichtung ist bereits abgeschlossen. Bitte melde dich an.")
    form = SetupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        # The first statement acquires the database write lock. The conditional
        # update also serializes contenders on databases with row-level locking.
        with transaction.atomic():
            claimed = Installation.objects.filter(pk=1, completed=False).update(completed=True)
            if not claimed or User.objects.filter(is_superuser=True).exists():
                return HttpResponseForbidden("Die Ersteinrichtung ist bereits abgeschlossen. Bitte melde dich an.")
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True
            user.save()
        login(request, user)
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        return redirect("manage_home")
    return render(request, "registration/setup.html", {"form": form})
