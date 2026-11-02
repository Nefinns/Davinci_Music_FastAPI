from supertokens_python.recipe.userroles.asyncio import create_new_role_or_add_permissions

# Capacidades de autenticación/perfil; no se inventan módulos comerciales.
ROLES = {
    "cliente": ["perfil:leer"],
    "maestro": ["perfil:leer"],
    "administrador": ["perfil:leer", "usuarios:roles:administrar"],
}

async def preparar_roles():
    for rol, permisos in ROLES.items():
        await create_new_role_or_add_permissions(rol, permisos)
