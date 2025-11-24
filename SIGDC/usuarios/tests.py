from django.test import TestCase
from django.conf import settings
import os


class SecurityTemplatesTests(TestCase):
	"""Checks to help prevent accidental XSS regressions in templates/code.

	- No usage of the `|safe` template filter in project templates.
	- No `{% autoescape off %}` blocks in templates.
	- No `mark_safe(` calls in Python code.
	These are conservative checks to fail fast during CI/dev runs.
	"""

	def test_no_safe_filter_in_templates(self):
		base = settings.BASE_DIR
		templates_root = os.path.join(base, 'templates')
		found = []
		for root, _, files in os.walk(templates_root):
			for fn in files:
				if not fn.endswith('.html'):
					continue
				p = os.path.join(root, fn)
				try:
					with open(p, 'r', encoding='utf-8') as f:
						txt = f.read()
				except Exception:
					continue
				if '|safe' in txt or '{% autoescape off %}' in txt:
					found.append(p)
		self.assertFalse(found, msg=f'Templates using |safe or autoescape off found: {found}')

	def test_no_mark_safe_in_python(self):
		base = settings.BASE_DIR
		found = []
		for root, _, files in os.walk(base):
			for fn in files:
				if not fn.endswith('.py'):
					continue
				p = os.path.join(root, fn)
				# skip virtualenv and migrations folders
				if 'venv' in p.split(os.sep) or 'migrations' in p.split(os.sep):
					continue
				try:
					with open(p, 'r', encoding='utf-8') as f:
						txt = f.read()
				except Exception:
					continue
				if 'mark_safe(' in txt:
					found.append(p)
		self.assertFalse(found, msg=f'Python files using mark_safe found: {found}')


class SecuritySQLTests(TestCase):
	
	def test_no_raw_sql_apis_used(self):
		base = settings.BASE_DIR
		found = []
		patterns = [
			'.extra(',
			'objects.raw(',
			'RawSQL',
			'connection.cursor(',
			'cursor.execute('
		]

		for root, _, files in os.walk(base):
			for fn in files:
				if not fn.endswith('.py'):
					continue
				p = os.path.join(root, fn)
				# skip virtualenv and migrations folders
				parts = p.split(os.sep)
				if 'venv' in parts or 'migrations' in parts:
					continue
				try:
					with open(p, 'r', encoding='utf-8') as f:
						txt = f.read()
				except Exception:
					continue
				for pat in patterns:
					if pat in txt:
						found.append((p, pat))
		self.assertFalse(found, msg=f'Potential raw SQL usages found: {found}')


class AuthBehaviorTests(TestCase):
	"""Pruebas que demuestran el comportamiento de autenticación en admin y en la app pública.

	- Verifica que /admin/ está protegido y sólo accesible por usuarios staff/superuser.
	- Verifica que la vista protegida /usuarios/menu/ redirige cuando no hay sesión y permite acceso tras login.
	- Verifica que el endpoint de logout redirige correctamente.
	"""

	def setUp(self):
		from django.contrib.auth.models import User
		# usuario normal
		self.user = User.objects.create_user(username='normal', email='normal@example.com', password='testpass123')
		# usuario administrador (staff + superuser)
		self.admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass123')

	def test_admin_access_restriction(self):
		c = self.client
		# anon -> redirige al login del admin
		resp = c.get('/admin/')
		self.assertIn(resp.status_code, (302, 301))
		self.assertIn('/admin/login', resp['Location'])

		# login con usuario normal -> sigue sin acceso (redirige al login del admin)
		logged = c.login(username='normal', password='testpass123')
		self.assertTrue(logged)
		resp2 = c.get('/admin/')
		# usuario sin is_staff no debe ver el panel (redirige a login)
		self.assertIn(resp2.status_code, (302, 301))
		self.assertIn('/admin/login', resp2['Location'])

		# login como admin staff -> acceso 200
		c.logout()
		logged_admin = c.login(username='admin', password='adminpass123')
		self.assertTrue(logged_admin)
		resp3 = c.get('/admin/')
		self.assertEqual(resp3.status_code, 200)
		self.assertIn(b'Django administration', resp3.content[:200])

	def test_public_login_and_protected_view(self):
		c = self.client
		# Vista protegida /usuarios/menu/ requiere login
		r = c.get('/usuarios/menu/')
		self.assertIn(r.status_code, (302, 301))

		# Iniciar sesión mediante la vista pública (index -> login)
		# La vista acepta 'email' o username en el campo 'email'
		resp = c.post('/usuarios/login/', {'email': 'normal', 'password': 'testpass123'}, follow=True)
		# tras login debería redirigir (se espera un 200 final)
		self.assertEqual(resp.status_code, 200)

		# Ahora la vista protegida debe ser accesible
		r2 = c.get('/usuarios/menu/')
		self.assertEqual(r2.status_code, 200)

		# Logout público
		lo = c.get('/usuarios/logout/', follow=True)
		self.assertIn(lo.status_code, (200, 302))
		# tras logout, acceso a menu debe redirigir de nuevo
		r3 = c.get('/usuarios/menu/')
		self.assertIn(r3.status_code, (302, 301))

