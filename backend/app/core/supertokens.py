from supertokens_python import init, InputAppInfo, SupertokensConfig

from supertokens_python.recipe import (
    accountlinking,
    emailpassword,
    session,
    thirdparty,
    userroles,
)
from supertokens_python.recipe.thirdparty import (
    ProviderInput,
    ProviderConfig,
    ProviderClientConfig,
    SignInAndUpFeature,
)

from supertokens_python.recipe.accountlinking.types import (
    ShouldAutomaticallyLink,
    ShouldNotAutomaticallyLink,
)

from app.core.config import (
    API_DOMAIN,
    FRONTEND_URL,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    SUPERTOKENS_CONNECTION_URI,
    SUPERTOKENS_API_KEY,
)


def disable_emailpassword_apis(original):
    # Los endpoints adaptadores validan el perfil y la vinculación local.
    # Desactivar las rutas alternativas evita saltarse estas comprobaciones.
    original.disable_sign_up_post = True
    original.disable_sign_in_post = True
    original.disable_email_exists_get = True
    original.disable_generate_password_reset_token_post = True
    original.disable_password_reset_post = True
    return original


async def decidir_vinculacion(
    nueva_cuenta,
    usuario_destino,
    sesion_actual,
    tenant_id,
    user_context,
):
    # Una cuenta nueva puede convertirse en usuario principal.
    if usuario_destino is None:
        return ShouldAutomaticallyLink(
            should_require_verification=True
        )

    # Una cuenta existente solo admite otro método si el propietario
    # ya inició sesión en esa misma cuenta y en el mismo tenant.
    if (
        sesion_actual is not None
        and sesion_actual.get_user_id() == usuario_destino.id
        and sesion_actual.get_tenant_id() == tenant_id
    ):
        return ShouldAutomaticallyLink(
            should_require_verification=True
        )

    return ShouldNotAutomaticallyLink()


def configurar_supertokens():
    init(
        app_info=InputAppInfo(
            app_name="DaVinciMusic",
            api_domain=API_DOMAIN,
            website_domain=FRONTEND_URL,
            api_base_path="/auth",
        ),
        supertokens_config=SupertokensConfig(
            connection_uri=SUPERTOKENS_CONNECTION_URI,
            api_key=SUPERTOKENS_API_KEY,
        ),
        framework="fastapi",
        mode="asgi",
        telemetry=False,
        recipe_list=[
            emailpassword.init(
                override=emailpassword.InputOverrideConfig(
                    apis=disable_emailpassword_apis
                )
            ),
            thirdparty.init(
                sign_in_and_up_feature=SignInAndUpFeature(
                    providers=[
                        ProviderInput(
                            config=ProviderConfig(
                                third_party_id="google",
                                clients=[
                                    ProviderClientConfig(
                                        client_id=GOOGLE_CLIENT_ID,
                                        client_secret=GOOGLE_CLIENT_SECRET,
                                    )
                                ],
                            )
                        )
                    ]
                )
            ), accountlinking.init(
                should_do_automatic_account_linking=decidir_vinculacion,
            ),
            session.init(
                get_token_transfer_method=lambda request, for_create_new_session, user_context: "cookie",
                cookie_secure=API_DOMAIN.startswith("https://"),
                anti_csrf="VIA_CUSTOM_HEADER",
            ),
            userroles.init(
                skip_adding_roles_to_access_token=True,
                skip_adding_permissions_to_access_token=True,
            ),
        ],
    )
