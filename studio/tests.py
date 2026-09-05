import json
from copy import deepcopy
from django.contrib.auth.models import User
from django.test import TestCase, Client, override_settings
from .models import Project
from .schema import validate_document

def document():
    return {'version':1,'canvas':{'width':600,'height':650,'background':'#ffffff'},'objects':[{'id':'one','asset':'sprout-v1','x':300,'y':340,'scale':1,'rotation':0,'flipped':False,'variant':0,'colors':{k:'#aabbcc' for k in ['skin','hair','shirt','trousers','shoes','eyes','horns']}}]}

@override_settings(SECURE_SSL_REDIRECT=False, STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class StudioTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_superuser('Parent', password='parent-test-strong-384')
        cls.rika=User.objects.create_user('Rika',password='long-test-password-483')
        cls.other=User.objects.create_user('Other',password='other-test-password-482')
    def setUp(self):
        self.client.force_login(self.rika)
    def create(self):
        return self.client.post('/api/projects/',data=json.dumps({'name':'Waldfreund','document':document()}),content_type='application/json')
    def test_save_open_edit_and_second_device(self):
        response=self.create()
        self.assertEqual(response.status_code,201)
        data=response.json();url=f"/api/projects/{data['id']}/"
        second=Client();second.force_login(self.rika)
        self.assertEqual(second.get(url).json()['document'],document())
        data['name']='Sternfreund'
        self.assertEqual(second.put(url,data=json.dumps(data),content_type='application/json').json()['revision'],2)
        self.assertEqual(self.client.put(url,data=json.dumps(data),content_type='application/json').status_code,409)
        self.assertEqual(self.client.get(f"/editor/{data['id']}/").status_code,200)
    def test_ownership_for_all_operations(self):
        data=self.create().json();url=f"/api/projects/{data['id']}/"
        self.client.force_login(self.other)
        self.assertEqual(self.client.get('/api/projects/').json()['projects'],[])
        for method in ['get','put','delete']:
            self.assertEqual(getattr(self.client,method)(url).status_code,404)
        self.assertEqual(self.client.get(f"/editor/{data['id']}/").status_code,404)
    def test_delete(self):
        data=self.create().json()
        self.assertEqual(self.client.delete(f"/api/projects/{data['id']}/").status_code,200)
        self.assertEqual(Project.objects.count(),0)
    def test_invalid_documents(self):
        for value in [None, [], {}, {'version':99}]:
            self.assertEqual(self.client.post('/api/projects/',data=json.dumps({'name':'X','document':value}),content_type='application/json').status_code,400)
        for field,value in [('x',float('nan')),('scale',10),('asset','<script>'),('flipped','yes'),('colors',{'skin':'url(https://evil)'})]:
            doc=document();doc['objects'][0][field]=value
            with self.assertRaises(ValueError): validate_document(doc)
    def test_csrf_required(self):
        client=Client(enforce_csrf_checks=True);client.force_login(self.rika)
        self.assertEqual(client.post('/api/projects/',data='{}',content_type='application/json').status_code,403)
        client.get('/')
        token=client.cookies['csrftoken'].value
        self.assertEqual(client.post('/api/projects/',data=json.dumps({'name':'CSRF','document':document()}),content_type='application/json',HTTP_X_CSRFTOKEN=token).status_code,201)
    def test_anonymous_and_password_hash(self):
        self.client.logout()
        self.assertEqual(self.client.get('/api/projects/').status_code,302)
        self.assertNotEqual(self.rika.password,'long-test-password-483')
        self.assertTrue(self.rika.check_password('long-test-password-483'))
    def test_login_logout_and_throttling(self):
        self.client.logout()
        self.assertEqual(self.client.post('/login/',{'username':'Rika','password':'long-test-password-483'}).status_code,302)
        self.assertEqual(self.client.get('/').status_code,200)
        self.assertEqual(self.client.get('/logout/').status_code,405)
        self.client.post('/logout/')
        for _ in range(10): self.client.post('/login/',{'username':'Rika','password':'wrong'})
        self.assertEqual(self.client.post('/login/',{'username':'Rika','password':'wrong'}).status_code,429)
    def test_names_are_escaped_and_headers_present(self):
        Project.objects.create(owner=self.rika,name='<script>alert(1)</script>',document=document())
        response=self.client.get('/')
        self.assertContains(response,'&lt;script&gt;')
        self.assertNotContains(response,'<script>alert(1)</script>')
        self.assertIn("object-src 'none'",response['Content-Security-Policy'])
