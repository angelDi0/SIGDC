from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class AdminAndPublicAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        # create a regular user
        self.user = User.objects.create_user(username='normal', password='pwd12345')
        # create a staff/superuser
        self.staff = User.objects.create_superuser(username='admin', password='adminpass', email='admin@example.com')

    def test_admin_access_requires_staff(self):
        # anonymous GET to admin should return 200 (admin login page)
        resp = self.client.get('/admin/')
        self.assertIn(resp.status_code, (200, 302))

        # login as normal user -> should NOT be allowed into admin index
        logged = self.client.login(username='normal', password='pwd12345')
        self.assertTrue(logged)
        resp = self.client.get('/admin/')
        # should redirect to admin login (or show login page) and not allow access
        self.assertNotEqual(resp.status_code, 200, msg="Non-staff user should not access admin index")

        # login as staff (superuser) -> should access admin index
        self.client.logout()
        logged = self.client.login(username='admin', password='adminpass')
        self.assertTrue(logged)
        resp = self.client.get('/admin/')
        self.assertEqual(resp.status_code, 200)

    def test_public_login_view_exists(self):
        # public login page should be reachable
        resp = self.client.get('/usuarios/login/')
        self.assertEqual(resp.status_code, 200)

    def test_protected_view_requires_login_and_redirects(self):
        # anonymous should be redirected to login when accessing /usuarios/menu/
        resp = self.client.get('/usuarios/menu/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp['Location'])

        # after login, the menu should be accessible
        logged = self.client.login(username='normal', password='pwd12345')
        self.assertTrue(logged)
        resp = self.client.get('/usuarios/menu/')
        self.assertEqual(resp.status_code, 200)