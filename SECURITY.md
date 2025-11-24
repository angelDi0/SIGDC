# Seguridad XSS — directrices para SIGDC

Este archivo resume las buenas prácticas y controles aplicados en el proyecto para prevenir Cross-Site Scripting (XSS).

1) Autoescape de Django
- Django habilita autoescaping por defecto en plantillas. No deshabilitarlo salvo que exista una justificación clara y revisada.
- Evitar `{% autoescape off %}` en plantillas.

2) No usar `|safe` ni `mark_safe` sin revisión
- No imprimir datos recibidos de usuarios con `|safe` en plantillas.
- No usar `django.utils.safestring.mark_safe` para inyectar HTML desde datos de usuario.
- Si se debe usar, documentar la razón y sanitizar/escapar antes.

3) Validación y serialización en servidor
- Para formularios Django usar `Form`/`ModelForm` y validar con `is_valid()`.
- Para APIs usar DRF `Serializer` y `is_valid()`; no confiar en la validación del cliente.

4) Sanitización en cliente
- En el JS, cuando se inserten datos en el DOM, usar funciones de escape (p.ej. `escapeHtml`) en vez de `innerHTML` con contenido sin sanitizar.
- Preferir textContent o createElement/textNode cuando sea posible.

5) Pruebas automáticas
- Se añadió una prueba en `usuarios/tests.py` que detecta usos accidentales de `|safe`, `{% autoescape off %}` o `mark_safe(`. Esta prueba ayuda a bloquear regresiones.

6) Buenas prácticas adicionales
- Considerar políticas CSP (Content-Security-Policy) para mitigar XSS a nivel de navegador.
- Escapar cualquier dato interpolado en cadenas HTML en JS.
- Revisar regularmente plantillas y puntos donde se construyen HTML dinámicamente.

Si necesitas que aplique una política CSP o que convierta algunas inserciones `innerHTML` a `textContent`/DOM-safe operations, lo implemento en el siguiente paso.