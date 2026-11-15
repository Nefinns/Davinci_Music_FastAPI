from supertokens_python import init, InputAppInfo, SupertokensConfig

from supertokens_python.recipe import (
    accountlinking,
    emailpassword,
    session,
    thirdparty,
    userroles,
    dashboard,
    emailverification
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

import asyncio
import time
from typing import Any

import jwt
from supertokens_python.recipe.thirdparty.provider import Provider

from supertokens_python.recipe.session.exceptions import TryRefreshTokenError
from supertokens_python.recipe.session.interfaces import RecipeInterface


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


def tolerar_desfase_google(provider: Provider) -> Provider:
    obtener_info_original = provider.get_user_info

    async def obtener_info(
        oauth_tokens: dict[str, Any],
        user_context: dict[str, Any],
    ):
        id_token = oauth_tokens.get("id_token")

        if isinstance(id_token, str):
            try:
                # Solo se lee iat para decidir cuánto esperar.
                # Esta lectura NO autentica al usuario.
                datos = jwt.decode(
                    id_token,
                    options={
                        "verify_signature": False,
                        "verify_exp": False,
                        "verify_iat": False,
                        "verify_nbf": False,
                        "verify_aud": False,
                    },
                )
                iat = datos.get("iat")

                if isinstance(iat, (int, float)) and not isinstance(iat, bool):
                    espera = iat - time.time()

                    if 0 < espera <= 2:
                        await asyncio.sleep(espera + 0.1)
            except (jwt.InvalidTokenError, ValueError, TypeError):
                # SuperTokens hará la validación y rechazará el token inválido.
                pass

        return await obtener_info_original(oauth_tokens, user_context)

    provider.get_user_info = obtener_info
    return provider


def tolerar_desfase_sesion(original: RecipeInterface) -> RecipeInterface:
    obtener_sesion_original = original.get_session

    async def obtener_sesion(
        access_token,
        anti_csrf_token=None,
        anti_csrf_check=None,
        session_required=None,
        check_database=None,
        override_global_claim_validators=None,
        user_context=None,
    ):
        async def verificar():
            return await obtener_sesion_original(
                access_token=access_token,
                anti_csrf_token=anti_csrf_token,
                anti_csrf_check=anti_csrf_check,
                session_required=session_required,
                check_database=check_database,
                override_global_claim_validators=override_global_claim_validators,
                user_context=user_context,
            )

        try:
            return await verificar()
        except TryRefreshTokenError as error:
            if str(error) != "The token is not yet valid (iat)":
                raise

            if not isinstance(access_token, str):
                raise

            try:
                # Se lee iat exclusivamente para calcular una espera.
                # Esta lectura NO valida ni autentica el token.
                payload = jwt.decode(
                    access_token,
                    options={
                        "verify_signature": False,
                        "verify_exp": False,
                        "verify_iat": False,
                        "verify_nbf": False,
                        "verify_aud": False,
                    },
                )
                iat = payload.get("iat")
            except (jwt.InvalidTokenError, ValueError, TypeError):
                raise error

            if isinstance(iat, bool) or not isinstance(iat, (int, float)):
                raise error

            espera = iat - time.time()
            if not 0 < espera <= 2:
                raise error

            await asyncio.sleep(espera + 0.1)
            return await verificar()

    original.get_session = obtener_sesion
    return original


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
                            ),
                            override=tolerar_desfase_google,
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
                override=session.SessionOverrideConfig(
                functions=tolerar_desfase_sesion,
            ),),
            userroles.init(
                skip_adding_roles_to_access_token=True,
                skip_adding_permissions_to_access_token=True,
            ),
            dashboard.init(),
            emailverification.init(mode="OPTIONAL")
        ],
    )
