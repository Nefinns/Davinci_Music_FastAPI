from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import emailpassword, session, userroles
from app.core.config import API_DOMAIN, FRONTEND_URL, SUPERTOKENS_CONNECTION_URI, SUPERTOKENS_API_KEY

def disable_emailpassword_apis(original):
    # Los endpoints adaptadores validan el perfil y la vinculación local.
    # Desactivar las rutas alternativas evita saltarse estas comprobaciones.
    original.disable_sign_up_post = True
    original.disable_sign_in_post = True
    original.disable_email_exists_get = True
    original.disable_generate_password_reset_token_post = True
    original.disable_password_reset_post = True
    return original

def configurar_supertokens():
    init(
        app_info=InputAppInfo(app_name="DaVinciMusic", api_domain=API_DOMAIN,
                              website_domain=FRONTEND_URL, api_base_path="/auth"),
        supertokens_config=SupertokensConfig(connection_uri=SUPERTOKENS_CONNECTION_URI,
                                             api_key=SUPERTOKENS_API_KEY),
        framework="fastapi", mode="asgi", telemetry=False,
        recipe_list=[
            emailpassword.init(override=emailpassword.InputOverrideConfig(apis=disable_emailpassword_apis)),
            session.init(get_token_transfer_method=lambda request, for_create_new_session, user_context: "cookie",
                         cookie_secure=API_DOMAIN.startswith("https://"), anti_csrf="VIA_CUSTOM_HEADER"),
            userroles.init(skip_adding_roles_to_access_token=True,
                           skip_adding_permissions_to_access_token=True),
        ],
    )
