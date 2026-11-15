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
    TENANT_ID,
)

import asyncio
import time
from typing import Any

import jwt
from supertokens_python.recipe.thirdparty.provider import Provider

from supertokens_python.recipe.session.exceptions import TryRefreshTokenError
from supertokens_python.recipe.session.interfaces import RecipeInterface

from sqlmodel import Session, select
from supertokens_python.asyncio import get_user
from supertokens_python.types import GeneralErrorResponse

from app.db.session import engine
from app.models.usuario import Usuario


def disable_emailpassword_apis(original):
    # El registro convencional sigue pasando por /auth/registro.
    # /auth/signup solo se habilita para añadir contraseña a una
    # cuenta Google autenticada y con perfil local completo.
    original_sign_up_post = original.sign_up_post

    async def sign_up_post(
        form_fields,
        tenant_id,
        session,
        should_try_linking_with_session_user,
        api_options,
        user_context,
    ):   
        if (
            session is None
            or tenant_id != TENANT_ID
            or session.get_tenant_id() != TENANT_ID
            or should_try_linking_with_session_user is not True
        ):
            return GeneralErrorResponse(
                message="Se requiere una sesión activa para agregar contraseña."
            )

        valores = {campo.id: campo.value for campo in form_fields}
        correo = valores.get("email")
        if not isinstance(correo, str):
            return GeneralErrorResponse(message="Correo inválido.")

        cuenta = await get_user(session.get_user_id())
        if cuenta is None or not any(
            metodo.recipe_id == "thirdparty"
            and metodo.third_party is not None
            and metodo.third_party.id == "google"
            and metodo.verified
            and tenant_id in metodo.tenant_ids
            and metodo.has_same_email_as(correo)
            for metodo in cuenta.login_methods
        ):
            return GeneralErrorResponse(
                message="Se requiere un correo Google verificado."
            )

        if any(
            metodo.recipe_id == "emailpassword"
            and tenant_id in metodo.tenant_ids
            for metodo in cuenta.login_methods
        ):
            return GeneralErrorResponse(
                message="La cuenta ya tiene contraseña."
            )

        with Session(engine) as db:
            perfil = db.exec(
                select(Usuario).where(
                    Usuario.identidad_externa == session.get_user_id()
                )
            ).first()

            if (
                perfil is None
                or not perfil.activo
                or perfil.correo.strip().lower() != correo.strip().lower()
            ):
                return GeneralErrorResponse(
                    message="El perfil no está disponible."
                )

        return await original_sign_up_post(
            form_fields,
            tenant_id,
            session,
            should_try_linking_with_session_user,
            api_options,
            user_context,
        )

    original.sign_up_post = sign_up_post
    original.disable_sign_up_post = False
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
