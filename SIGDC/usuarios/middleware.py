from django.conf import settings
from django.shortcuts import redirect


class LoginRequiredMiddleware:
    """
    Middleware simple que fuerza login para la mayoría de URLs.

    Comportamiento:
    - Si el usuario ya está autenticado, deja pasar la petición.
    - Si la ruta comienza con alguno de los prefijos definidos en
      settings.LOGIN_EXEMPT_URLS, deja pasar la petición.
    - En caso contrario, redirige a settings.LOGIN_URL con parámetro next.

    Para que `request.user` exista, esta middleware debe aparecer *después*
    de 'django.contrib.auth.middleware.AuthenticationMiddleware' en MIDDLEWARE.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Lista de prefijos exentos (normalizados sin slash inicial)
        exempt = getattr(settings, 'LOGIN_EXEMPT_URLS', [])
        # Asegurar que LOGIN_URL está en las exenciones
        login_url = getattr(settings, 'LOGIN_URL', '/usuarios/login/')
        # normalizar para comparaciones (sin slash inicial)
        normalized = [u.lstrip('/') for u in exempt]
        normalized.append(login_url.lstrip('/'))
        # siempre eximir admin login y static/media por defecto
        normalized.extend(['admin/', 'static/', 'media/'])
        # deduplicación simple
        self.exempt_prefixes = list(dict.fromkeys(normalized))

    def __call__(self, request):
        path = request.path_info.lstrip('/')  # quitar slash inicial para startswith

        # Si el usuario ya está autenticado, dejar pasar
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return self.get_response(request)

        # Comprobar exenciones por prefijo
        for prefix in self.exempt_prefixes:
            if prefix == '':
                continue
            if path.startswith(prefix):
                return self.get_response(request)

        # No autenticado y no exento -> redirigir al login con next
        login_url = getattr(settings, 'LOGIN_URL', '/usuarios/login/')
        # mantener querystring next con la ruta original
        return redirect(f"{login_url}?next={request.path}")
