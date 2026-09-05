import io
import json
from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from .models import Photo
from .test_setup import SETTINGS
from .test_spaces import space, item
from .photos import normalize


def image_file(size=(80,40), fmt='JPEG'):
    output=io.BytesIO()
    image=Image.new('RGB',size,'red')
    exif=Image.Exif();exif[270]='private metadata';exif[274]=6
    image.save(output,format=fmt,exif=exif)
    return SimpleUploadedFile('table.jpg',output.getvalue(),content_type='image/jpeg')

@override_settings(**SETTINGS)
class PhotoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user=User.objects.create_superuser('Parent',password='parent-test-384')
        cls.other=User.objects.create_user('Other',password='other-test-384')
    def setUp(self): self.client.force_login(self.user)
    def upload(self): return self.client.post('/api/photos/',{'photo':image_file(),'name':'Mein Tisch','crop':'[0,0,1,1]'})
    def test_normalization_and_metadata_removed(self):
        response=self.upload();self.assertEqual(response.status_code,201)
        p=response.json();self.assertEqual((p['width'],p['height']),(40,80))
        photo=Photo.objects.get(pk=p['id'])
        with Image.open(io.BytesIO(bytes(photo.content))) as image:
            self.assertFalse(image.getexif());self.assertEqual(image.format,'JPEG')
        response=self.client.get(f"/api/photos/{p['id']}/image/")
        self.assertEqual(response.status_code,200)
        self.assertEqual(response['Cache-Control'],'private, no-store')
    def test_resize_and_crop(self):
        content,w,h=normalize(image_file((2400,1200)),[0,.25,1,.75])
        self.assertLessEqual(max(w,h),1600)
        self.assertEqual(w,h)  # Orientation applied before crop.
    def test_invalid_formats_and_crop(self):
        for data in [b'<svg onload="alert(1)"></svg>',b'not an image']:
            response=self.client.post('/api/photos/',{'photo':SimpleUploadedFile('a.jpg',data),'name':'X'})
            self.assertEqual(response.status_code,400)
        for crop in ['null','{}','[0,0,0,1]','[0,0,NaN,1]','[-1,0,1,1]']:
            self.assertEqual(self.client.post('/api/photos/',{'photo':image_file(),'name':'X','crop':crop}).status_code,400)
        self.assertFalse(Photo.objects.exists())
    def test_private_images_and_project_references(self):
        p=self.upload().json()
        doc=space();obj=item('photo-v1');obj['photo']={k:p[k] for k in ['id','width','height']};doc['objects']=[obj]
        payload={'name':'Fotozimmer','kind':'room','document':doc}
        self.assertEqual(self.client.post('/api/projects/',data=json.dumps(payload),content_type='application/json').status_code,201)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get('/api/photos/').json()['photos'],[])
        self.assertEqual(self.client.get(f"/api/photos/{p['id']}/image/").status_code,404)
        self.assertEqual(self.client.post('/api/projects/',data=json.dumps(payload),content_type='application/json').status_code,400)
        self.client.logout()
        self.assertEqual(self.client.get(f"/api/photos/{p['id']}/image/").status_code,302)
    def test_csrf_and_limits(self):
        client=Client(enforce_csrf_checks=True);client.force_login(self.user)
        self.assertEqual(client.post('/api/photos/',{'photo':image_file(),'name':'X'}).status_code,403)
        Photo.objects.bulk_create([Photo(owner=self.user,name='X',width=1,height=1,content=b'x') for _ in range(100)])
        self.assertEqual(self.upload().status_code,400)
    def test_oversized_file(self):
        photo=image_file();photo.size=13*1024*1024
        with self.assertRaises(ValueError): normalize(photo,[0,0,1,1])
    def test_delete_unused_and_reject_foreign(self):
        p=self.upload().json();url=f"/api/photos/{p['id']}/"
        self.client.force_login(self.other)
        self.assertEqual(self.client.delete(url).status_code,404)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(url).status_code,405)
        csrf=Client(enforce_csrf_checks=True);csrf.force_login(self.user)
        self.assertEqual(csrf.delete(url).status_code,403)
        self.assertEqual(self.client.delete(url).status_code,200)
        self.assertFalse(Photo.objects.filter(pk=p['id']).exists())
        self.assertEqual(self.client.get(url+'image/').status_code,404)

    def test_delete_used_photo_requires_removing_saved_reference(self):
        from .models import Project
        p=self.upload().json();doc=space();obj=item('photo-v1');obj['photo']={k:p[k] for k in ['id','width','height']};doc['objects']=[obj]
        project=Project.objects.create(owner=self.user,name='Mein Fotozimmer',kind='room',document=doc)
        url=f"/api/photos/{p['id']}/"
        response=self.client.delete(url)
        self.assertEqual(response.status_code,409)
        self.assertIn('Mein Fotozimmer',response.json()['error'])
        project.document=space();project.save()
        self.assertEqual(self.client.delete(url).status_code,200)
        payload={'name':'Alter Tab','kind':'room','document':doc}
        self.assertEqual(self.client.post('/api/projects/',data=json.dumps(payload),content_type='application/json').status_code,400)
