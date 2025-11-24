from django.test import TestCase, Client
from django.contrib.auth.models import User
from usuarios.models import Perfil
from .models import Solicitud


class SolicitudPermissionsTests(TestCase):
    def setUp(self):
        # usuario propietario
        self.owner_user = User.objects.create_user(username='owner', password='pass')
        self.owner_perfil = Perfil.objects.create(usuario='owner', email='owner@example.com')

        # usuario admin
        self.admin_user = User.objects.create_user(username='admin', password='pass', is_staff=True, is_superuser=True)
        self.admin_perfil = Perfil.objects.create(usuario='admin', email='admin@example.com')

        # otro usuario
        self.other_user = User.objects.create_user(username='other', password='pass')
        self.other_perfil = Perfil.objects.create(usuario='other', email='other@example.com')

        # crear solicitud asociada al owner_perfil
        self.solicitud = Solicitud.objects.create(titulo='Prueba', solicitante=self.owner_perfil)

        self.client = Client()

    def test_owner_can_access_edit(self):
        self.client.login(username='owner', password='pass')
        resp = self.client.get(f'/solicitudes/{self.solicitud.pk}/editar/')
        self.assertEqual(resp.status_code, 200)

    def test_admin_can_access_edit(self):
        self.client.login(username='admin', password='pass')
        resp = self.client.get(f'/solicitudes/{self.solicitud.pk}/editar/')
        self.assertEqual(resp.status_code, 200)

    def test_other_cannot_access_edit(self):
        self.client.login(username='other', password='pass')
        resp = self.client.get(f'/solicitudes/{self.solicitud.pk}/editar/')
        self.assertIn(resp.status_code, (302, 403))
        # depending on middleware, might redirect to login or return 403
