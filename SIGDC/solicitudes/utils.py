def user_can_access_solicitud(user, solicitud):
    """
    Regla de comunicación segura entre apps:
    - superuser y staff siempre tienen acceso
    - usuarios con permiso change_solicitud o delete_solicitud también
    - el dueño (solicitante.usuario == user.username) también
    """
    if not user.is_authenticated:
        return False

    if user.is_staff or user.is_superuser:
        return True

    if user.has_perm("solicitudes.change_solicitud") or user.has_perm("solicitudes.delete_solicitud"):
        return True

    solicitante = getattr(solicitud, "solicitante", None)
    if not solicitante:
        return False

    if str(solicitante.usuario) == str(user.username):
        return True

    if hasattr(solicitante, "email") and solicitante.email == user.email:
        return True

    return False