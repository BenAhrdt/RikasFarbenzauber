import json
from copy import deepcopy
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from .schema import validate_document, ASSETS
from .tests import document
from .test_setup import SETTINGS

def space():
    return {'version':2,'canvas':{'width':900,'height':650,'background':'#dceef6','ground':'#c3d5a6'},'objects':[]}

def item(asset='house-v1'):
    return {'id':'one','asset':asset,'x':800,'y':400,'scale':1,'rotation':15,'flipped':True,'variant':0,'colors':{'main':'#aabbcc','detail':'#ccddee','accent':'#aaffcc'}}

@override_settings(**SETTINGS)
class SpaceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent=User.objects.create_superuser('Parent', password='parent-test-384')
        cls.other=User.objects.create_user('Other', password='other-test-385')
    def setUp(self): self.client.force_login(self.parent)
    def save(self,kind,doc):
        return self.client.post('/api/projects/',data=json.dumps({'name':'Zauberort','kind':kind,'document':doc}),content_type='application/json')
    def test_types_and_reopening(self):
        for kind in ['room','world','scene']:
            doc=space();doc['objects']=[item()]
            response=self.save(kind,doc)
            self.assertEqual(response.status_code,201)
            p=response.json();self.assertEqual(p['kind'],kind)
            self.assertContains(self.client.get(f"/editor/{p['id']}/"),'space-editor')
            self.assertContains(self.client.get(f'/?kind={kind}'),'Zauberort')
            self.assertEqual(self.client.get(f"/api/projects/{p['id']}/").json()['document'],doc)
            p['document']['objects'][0]['x']=100
            self.assertEqual(self.client.put(f"/api/projects/{p['id']}/",data=json.dumps(p),content_type='application/json').status_code,200)
    def test_all_assets_and_limits(self):
        for asset in ASSETS - {"photo-v1"}:
            doc=space();doc['objects']=[item(asset)];validate_document(doc)
        doc=space();doc['objects']=[{**item(),'id':str(i)} for i in range(100)]
        self.assertEqual(self.save('room',doc).status_code,201)
        doc['objects'].append({**item(),'id':'101'})
        self.assertEqual(self.save('room',doc).status_code,400)
    def test_ownership(self):
        p=self.save('world',space()).json()
        self.client.force_login(self.other)
        for method in ['get','put','delete']:
            self.assertEqual(getattr(self.client,method)(f"/api/projects/{p['id']}/").status_code,404)
        self.assertEqual(self.client.get(f"/editor/{p['id']}/").status_code,404)
    def test_versions_and_malicious_values(self):
        self.assertEqual(self.save('room',document()).status_code,400)
        self.assertEqual(self.save('character',space()).status_code,400)
        self.assertEqual(self.save('invented',space()).status_code,400)
        for value in ['url(javascript:alert(1))',None,{},'#abc']:
            doc=space();doc['canvas']['ground']=value
            self.assertEqual(self.save('world',doc).status_code,400)
        doc=space();doc['objects']=[item('unknown')]
        self.assertEqual(self.save('world',doc).status_code,400)
    def test_figure_copies_in_scene(self):
        doc=space();doc['objects']=[document()['objects'][0],{**item(),'id':'house'}]
        self.assertEqual(self.save('scene',doc).status_code,201)
        self.assertEqual(self.save('character',document()).status_code,201)

    def test_free_drawing_is_saved_and_reopened(self):
        doc=space();doc['canvas']['plain']=True;doc['strokes']=[{'id':'line-one','color':'#7561be','width':9,'points':[[10,20],[30.5,40]]}]
        response=self.save('drawing',doc)
        self.assertEqual(response.status_code,201)
        saved=response.json()
        self.assertEqual(saved['document']['strokes'],doc['strokes'])
        self.assertContains(self.client.get('/?kind=drawing'),'Zeichnung')
        self.assertContains(self.client.get(f"/editor/{saved['id']}/"),'data-kind="drawing"')

    def test_invalid_drawing_data_is_rejected(self):
        cases=[
            [{'id':'x','color':'red','width':9,'points':[[10,20]]}],
            [{'id':'x','color':'#112233','width':0,'points':[[10,20]]}],
            [{'id':'x','color':'#112233','width':9,'points':[[901,20]]}],
        ]
        for strokes in cases:
            doc=space();doc['strokes']=strokes
            self.assertEqual(self.save('drawing',doc).status_code,400)
