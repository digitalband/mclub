from api_v1.auth.services import AuthService


def auth_service_depends() -> AuthService:
    return AuthService()
