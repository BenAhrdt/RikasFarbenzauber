from django.contrib.auth.models import User
from django.test import TestCase, Client
from .models import UserAccess

class ImpersonationTests(TestCase):
    def setUp(self):
        self.admin=User.objects.create_superuser('admin',password='strong-password-82')
        self.child=User.objects.create_user('child',password='strong-password-83')
        UserAccess.objects.create(user=self.child,rooms=False)
        self.client.force_login(self.admin)
        self.start=f'/verwaltung/benutzer/{self.child.pk}/anmelden/'

    def test_switch_restricted_user_and_return(self):
        old=self.client.session.session_key
        self.assertRedirects(self.client.post(self.start),'/')
        self.assertNotEqual(old,self.client.session.session_key)
        self.assertEqual(int(self.client.session['_auth_user_id']),self.child.pk)
        self.assertContains(self.client.get('/'),'Zurück zum Admin')
        self.assertEqual(self.client.get('/editor/?kind=room').status_code,403)
        self.assertEqual(self.client.get('/verwaltung/').status_code,403)
        self.assertEqual(self.client.post(self.start).status_code,403)
        self.assertRedirects(self.client.post('/verwaltung/zurueck/'),'/verwaltung/benutzer/')
        self.assertEqual(int(self.client.session['_auth_user_id']),self.admin.pk)
        self.assertNotIn('acting_admin',self.client.session)

    def test_revocation_and_logout_remove_return(self):
        for revoke in ('password','inactive','demote','logout'):
            with self.subTest(revoke=revoke):
                self.admin.is_active=True;self.admin.is_superuser=True;self.admin.save()
                self.client.force_login(self.admin)
                self.client.post(self.start)
                if revoke=='password':self.admin.set_password('replacement-84');self.admin.save()
                if revoke=='inactive':self.admin.is_active=False;self.admin.save()
                if revoke=='demote':self.admin.is_superuser=False;self.admin.save()
                if revoke=='logout':self.client.post('/logout/')
                self.assertEqual(self.client.post('/verwaltung/zurueck/').status_code,403)
                self.assertNotIn('acting_admin',self.client.session)

    def test_post_csrf_and_no_child_escalation(self):
        self.assertEqual(self.client.get(self.start).status_code,405)
        secure=Client(enforce_csrf_checks=True);secure.force_login(self.admin)
        self.assertEqual(secure.post(self.start).status_code,403)
        self.client.force_login(self.child)
        self.assertEqual(self.client.post(self.start).status_code,403)
        self.assertEqual(self.client.post('/verwaltung/zurueck/').status_code,403)

    def test_disabled_target_and_browser_session(self):
        self.child.is_active=False;self.child.save()
        self.assertEqual(self.client.post(self.start).status_code,404)
        self.child.is_active=True;self.child.save()
        session=self.client.session;session.set_expiry(0);session.save()
        self.client.post(self.start)
        self.assertTrue(self.client.session.get_expire_at_browser_close())
        self.client.post('/verwaltung/zurueck/')
        self.assertTrue(self.client.session.get_expire_at_browser_close())
