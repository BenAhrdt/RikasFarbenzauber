import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from .models import UserAccess, Project
from .test_setup import SETTINGS
from .tests import document
from .test_spaces import space

@override_settings(**SETTINGS)
class ManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin=User.objects.create_superuser('Parent',password='Original-Strong-583!')
        cls.child=User.objects.create_user('Rika',password='Child-Strong-584!')
    def setUp(self):self.client.force_login(self.admin)
    def account_data(self,**extra):
        return {'username':'NewUser','first_name':'','is_active':'on','characters':'on','password1':'ZitronenMond-853!','password2':'ZitronenMond-853!',**extra}
    def test_custom_admin_and_create_rights(self):
        self.assertContains(self.client.get('/verwaltung/'),'Deine Verwaltung')
        response=self.client.post('/verwaltung/benutzer/neu/',self.account_data())
        self.assertEqual(response.status_code,302)
        user=User.objects.get(username='NewUser')
        self.assertTrue(user.access.characters)
        self.assertFalse(user.access.rooms)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password('ZitronenMond-853!'))
    def test_administration_is_admin_only(self):
        self.client.force_login(self.child)
        for path in ['/verwaltung/','/verwaltung/benutzer/','/verwaltung/benutzer/neu/','/verwaltung/updates/','/verwaltung/updates/status/']:
            self.assertEqual(self.client.get(path).status_code,403)
        self.assertEqual(self.client.post('/verwaltung/updates/check/').status_code,403)
        self.assertEqual(self.client.post('/verwaltung/updates/install/').status_code,403)
    def test_content_permissions_enforced_in_api(self):
        UserAccess.objects.create(user=self.child,characters=True,rooms=False,worlds=False,scenes=False,photos=False,delete_projects=False)
        room=Project.objects.create(owner=self.child,name='Raum',kind='room',document=space())
        figure=Project.objects.create(owner=self.child,name='Figur',document=document())
        self.client.force_login(self.child)
        self.assertEqual(self.client.get('/editor/?kind=room').status_code,403)
        self.assertEqual(self.client.get(f'/api/projects/{room.pk}/').status_code,403)
        self.assertEqual(len(self.client.get('/api/projects/').json()['projects']),1)
        self.assertEqual(self.client.post('/api/projects/',data=json.dumps({'name':'X','kind':'room','document':space()}),content_type='application/json').status_code,403)
        self.assertEqual(self.client.delete(f'/api/projects/{figure.pk}/').status_code,403)
        self.assertEqual(self.client.get('/api/photos/').status_code,403)
    def test_admin_cannot_lock_themselves_out(self):
        response=self.client.post(f'/verwaltung/benutzer/{self.admin.pk}/',{'username':'Parent'})
        self.assertEqual(response.status_code,200)
        self.admin.refresh_from_db();self.assertTrue(self.admin.is_active and self.admin.is_superuser)
    def test_deactivated_account_loses_access(self):
        self.client.force_login(self.child)
        User.objects.filter(pk=self.child.pk).update(is_active=False)
        self.assertEqual(self.client.get('/api/projects/').status_code,302)
    def test_remembered_session_and_logout(self):
        client=Client()
        response=client.post('/login/',{'username':'Rika','password':'Child-Strong-584!','remember':'on'})
        self.assertEqual(response.status_code,302)
        self.assertGreater(int(response.cookies['sessionid']['max-age']),300*86400)
        another_browser=Client();another_browser.cookies['sessionid']=client.cookies['sessionid'].value
        self.assertEqual(another_browser.get('/').status_code,200)
        client.post('/logout/')
        self.assertEqual(another_browser.get('/api/projects/').status_code,302)
        client.post('/login/',{'username':'Rika','password':'Child-Strong-584!'})
        self.assertTrue(client.session.get_expire_at_browser_close())
    def test_update_check_and_atomic_request(self):
        release={'version':'9.0.0','url':'https://updates.example.org/release.zip','sha256':'a'*64,'notes':'Neu'}
        with tempfile.TemporaryDirectory() as folder,override_settings(UPDATE_STATE_DIR=Path(folder),UPDATE_INSTALL_ENABLED=True,UPDATE_MANIFEST_URL='https://updates.example.org/latest.json'),patch('studio.updates.manifest',return_value=release):
            self.assertTrue(self.client.post('/verwaltung/updates/check/').json()['available'])
            response=self.client.post('/verwaltung/updates/install/',data=json.dumps({'version':'9.0.0'}),content_type='application/json')
            self.assertEqual(response.status_code,202)
            data=json.loads((Path(folder)/'request.json').read_text())
            self.assertEqual(set(data),{'version','sha256','job'})
            self.assertEqual(self.client.post('/verwaltung/updates/install/',data=json.dumps({'version':'9.0.0'}),content_type='application/json').status_code,409)
    def test_updates_without_source_and_csrf(self):
        with override_settings(UPDATE_MANIFEST_URL=''):
            self.assertEqual(self.client.post('/verwaltung/updates/check/').status_code,400)
        csrf=Client(enforce_csrf_checks=True);csrf.force_login(self.admin)
        self.assertEqual(csrf.post('/verwaltung/updates/install/').status_code,403)
