from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path
from studio import views, photos, administration, updates, impersonation, site_access
from django.views.generic import RedirectView
urlpatterns = [
    path('verwaltung/zugang/', site_access.configure, name='manage_access'),
    path('verwaltung/benutzer/<int:pk>/anmelden/', impersonation.start, name='impersonate_start'),
    path('verwaltung/zurueck/', impersonation.stop, name='impersonate_stop'),
    path("verwaltung/", administration.home, name="manage_home"),
    path("verwaltung/benutzer/", administration.users, name="manage_users"),
    path("verwaltung/benutzer/neu/", administration.account, name="manage_user_new"),
    path("verwaltung/benutzer/<int:pk>/", administration.account, name="manage_user"),
    path("verwaltung/updates/", updates.page, name="manage_updates"),
    path("verwaltung/updates/check/", updates.check),
    path("verwaltung/updates/install/", updates.install),
    path("verwaltung/updates/status/", updates.status),
    path("health/", updates.health),
path("api/photos/<uuid:pk>/", photos.delete_photo),path("api/photos/", photos.photos), path("api/photos/<uuid:pk>/image/", photos.photo_image),path("setup/", views.setup_view, name="setup"),path("admin/login/", views.login_view), path("admin/", RedirectView.as_view(pattern_name="manage_home", permanent=False)), path("admin/<path:unused>", RedirectView.as_view(pattern_name="manage_users", permanent=False)), path("login/", views.login_view, name="login"), path("logout/", LogoutView.as_view(), name="logout"), path("", views.dashboard, name="dashboard"), path("editor/", views.editor, name="new"), path("editor/<uuid:pk>/", views.editor, name="editor"), path("api/projects/", views.projects), path("api/projects/<uuid:pk>/", views.project)]
