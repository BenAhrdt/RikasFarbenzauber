from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from .models import Installation

SETTINGS = dict(SECURE_SSL_REDIRECT=False, STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})

def credentials(name='Eltern'):
    return {'username': name, 'password1': 'ZitronenWolke-482!Regen', 'password2': 'ZitronenWolke-482!Regen'}

@override_settings(**SETTINGS)
class SetupTests(TestCase):
    def test_first_visit_and_success(self):
        self.assertRedirects(self.client.get('/'), '/login/?next=/', fetch_redirect_response=False)
        self.assertRedirects(self.client.get('/login/'), '/setup/')
        response = self.client.post('/setup/', credentials())
        self.assertRedirects(response, '/verwaltung/')
        user = User.objects.get(username='Eltern')
        self.assertTrue(user.is_staff and user.is_superuser and user.check_password(credentials()['password1']))
        self.assertTrue(Installation.objects.get(pk=1).completed)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_permanent_lock_after_account_deletion(self):
        self.client.post('/setup/', credentials())
        self.client.logout()
        User.objects.all().delete()
        self.assertEqual(self.client.get('/setup/').status_code, 403)
        self.assertEqual(self.client.post('/setup/', credentials('Second')).status_code, 403)
        self.assertEqual(User.objects.count(), 0)

    def test_existing_admin_including_inactive_blocks_setup(self):
        User.objects.create_superuser('Existing', password='long-password-583', is_active=False)
        self.assertEqual(self.client.post('/setup/', credentials()).status_code, 403)
        self.assertTrue(Installation.objects.get(pk=1).completed)

    def test_invalid_password_does_not_consume_setup(self):
        data = credentials(); data['password2'] = 'different'
        self.assertEqual(self.client.post('/setup/', data).status_code, 200)
        self.assertFalse(Installation.objects.get(pk=1).completed)
        self.assertFalse(User.objects.exists())
        data['password1'] = data['password2'] = '123'
        self.client.post('/setup/', data)
        self.assertFalse(User.objects.exists())

    def test_csrf(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/setup/', credentials()).status_code, 403)
        client.get('/setup/')
        self.assertEqual(client.post('/setup/', credentials(), HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value).status_code, 302)

    def test_stale_form_cannot_create_second_admin(self):
        second = Client(); second.get('/setup/')
        self.client.post('/setup/', credentials())
        self.assertEqual(second.post('/setup/', credentials('Second')).status_code, 403)
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 1)
