import uuid
from django.conf import settings
from django.db import models
class Project(models.Model):
    class Kind(models.TextChoices):
        CHARACTER = "character", "Figur"
        ROOM = "room", "Raum"
        WORLD = "world", "Welt"
        SCENE = "scene", "Szene"
        DRAWING = "drawing", "Zeichnung"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.CHARACTER)
    document = models.JSONField()
    revision = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["owner", "-updated_at"])]
class LoginAttempt(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    count = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField()

class Installation(models.Model):
    """Permanent one-time bootstrap latch, independent of later account deletion."""
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    completed = models.BooleanField(default=False)

class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    content = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class UserAccess(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='access')
    characters = models.BooleanField(default=True)
    rooms = models.BooleanField(default=True)
    worlds = models.BooleanField(default=True)
    scenes = models.BooleanField(default=True)
    photos = models.BooleanField(default=True)
    delete_projects = models.BooleanField(default=True)

class SiteAccess(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    https_origins = models.JSONField(default=list)
