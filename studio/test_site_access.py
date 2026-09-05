from unittest.mock import patch
from django.test import TestCase, Client, override_settings
from django.conf import settings
from django.contrib.auth.models import User
from .models import SiteAccess
from .site_access import AccessForm

@override_settings(RIKA_LOCAL_ACCESS=True,ALLOWED_HOSTS=['*'],RIKA_HTTPS_ORIGINS=[],SECURE_SSL_REDIRECT=False,SESSION_COOKIE_SECURE=False,CSRF_COOKIE_SECURE=False,MIDDLEWARE=['studio.site_access.LocalAndHttps']+settings.MIDDLEWARE)
class SiteAccessTests(TestCase):
    def setUp(self):
        self.admin=User.objects.create_superuser('admin',password='secure-test-password-83')
        self.hosts=patch('studio.site_access.local_hosts',return_value={'127.0.0.1','localhost','192.168.2.131'})
        self.hosts.start();self.addCleanup(self.hosts.stop)

    def test_local_and_dynamic_https_allowlist(self):
        self.assertEqual(self.client.get('/login/',HTTP_HOST='192.168.2.131:8080').status_code,200)
        self.assertEqual(self.client.get('/login/',HTTP_HOST='unlisted.example.org',secure=True).status_code,403)
        self.client.force_login(self.admin)
        response=self.client.post('/verwaltung/zugang/',{'addresses':'https://farben.example.org\nhttps://other.example.org'},HTTP_HOST='192.168.2.131:8080')
        self.assertEqual(response.status_code,302)
        self.assertEqual(self.client.get('/login/',HTTP_HOST='farben.example.org',secure=True).status_code,200)
        self.assertEqual(self.client.get('/login/',HTTP_HOST='farben.example.org').status_code,403)
        self.client.post('/verwaltung/zugang/',{'addresses':''},HTTP_HOST='192.168.2.131:8080')
        self.assertEqual(self.client.get('/login/',HTTP_HOST='farben.example.org',secure=True).status_code,403)
        self.assertEqual(self.client.get('/verwaltung/zugang/',HTTP_HOST='192.168.2.131:8080').status_code,200)

    def test_separate_http_and_https_cookies_and_logout(self):
        SiteAccess.objects.create(https_origins=['https://farben.example.org'])
        response=self.client.post('/login/',{'username':'admin','password':'secure-test-password-83','remember':'on'},HTTP_HOST='farben.example.org',secure=True)
        self.assertIn('__Host-sessionid',response.cookies)
        self.assertTrue(response.cookies['__Host-sessionid']['secure'])
        self.assertNotIn('sessionid',response.cookies)
        self.assertEqual(self.client.get('/verwaltung/',HTTP_HOST='farben.example.org',secure=True).status_code,200)
        self.assertEqual(self.client.get('/verwaltung/',HTTP_HOST='192.168.2.131:8080').status_code,302)
        response=self.client.post('/logout/',HTTP_HOST='farben.example.org',secure=True)
        self.assertEqual(response.cookies['__Host-sessionid']['max-age'],0)

    def test_validation_and_admin_only(self):
        for value in ['http://example.org','https://example.org/path','https://user:pass@example.org','*.example.org']:
            self.assertFalse(AccessForm({'addresses':value}).is_valid())
        user=User.objects.create_user('child',password='test-83-password')
        self.client.force_login(user)
        self.assertEqual(self.client.post('/verwaltung/zugang/',{'addresses':'example.org'},HTTP_HOST='localhost').status_code,403)

    def test_https_csrf_remains_enforced(self):
        SiteAccess.objects.create(https_origins=['https://farben.example.org'])
        client=Client(enforce_csrf_checks=True)
        response=client.get('/login/',HTTP_HOST='farben.example.org',secure=True)
        token=response.cookies['__Host-csrftoken'].value
        data={'username':'admin','password':'secure-test-password-83'}
        self.assertEqual(client.post('/login/',data,HTTP_HOST='farben.example.org',secure=True,HTTP_X_CSRFTOKEN=token,HTTP_ORIGIN='https://evil.example.org').status_code,403)
        self.assertEqual(client.post('/login/',data,HTTP_HOST='farben.example.org',secure=True,HTTP_X_CSRFTOKEN=token,HTTP_ORIGIN='https://farben.example.org').status_code,302)
