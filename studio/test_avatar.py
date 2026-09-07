import json
from copy import deepcopy
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from .schema import CATALOG, validate_document
from .tests import document
from .test_spaces import space
from .test_setup import SETTINGS


def avatar_document():
    doc=document();o=doc['objects'][0]
    o['asset']='avatar-v2'
    o['colors']={k:v[1] for k,v in CATALOG['colors'].items()}
    o['appearance']={s:{k:v['default'] for k,v in CATALOG[s].items()} for s in ['choices','body']}
    return doc

@override_settings(**SETTINGS)
class AvatarTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user=User.objects.create_superuser('Parent',password='parent-test-384')
    def setUp(self): self.client.force_login(self.user)
    def test_every_choice_and_proportion_extreme(self):
        for key,spec in CATALOG['choices'].items():
            for value,label in spec['options']:
                doc=avatar_document();doc['objects'][0]['appearance']['choices'][key]=value
                validate_document(doc)
        for key,spec in CATALOG['body'].items():
            for value in [spec['min'],spec['max']]:
                doc=avatar_document();doc['objects'][0]['appearance']['body'][key]=value
                validate_document(doc)
    def test_reject_malformed_settings(self):
        for section,key,value in [('body','height',float('nan')),('body','head',99),('body','width',True),('choices','hair','<script>'),('choices','eyes',[]),('choices','hat','unknown')]:
            doc=avatar_document();doc['objects'][0]['appearance'][section][key]=value
            with self.assertRaises(ValueError):validate_document(doc)
        doc=avatar_document();del doc['objects'][0]['appearance']['choices']['hair']
        with self.assertRaises(ValueError):validate_document(doc)
    def test_save_reopen_scene_and_legacy(self):
        hunter=avatar_document()
        hunter['objects'][0]['appearance']['choices'].update(hair='longbraid',top='hunter',handheld='sword',faceDetail='runes',hat='foxmask')
        for doc in [document(),avatar_document(),hunter]:
            response=self.client.post('/api/projects/',data=json.dumps({'name':'Figur','document':doc}),content_type='application/json')
            self.assertEqual(response.status_code,201)
            p=response.json()
            self.assertEqual(self.client.get(f"/api/projects/{p['id']}/").json()['document'],doc)
            scene=space();scene['objects']=deepcopy(doc['objects'])
            self.assertEqual(self.client.post('/api/projects/',data=json.dumps({'name':'Szene','kind':'scene','document':scene}),content_type='application/json').status_code,201)
