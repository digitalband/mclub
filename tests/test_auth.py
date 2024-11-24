import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from api_v1.auth.utils import JWTHandler

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()


@pytest.fixture(
    params=[
        {"private_key": "key1", "public_key": "key1", "algorithm": "HS256"},
        {"private_key": private_key, "public_key": public_key, "algorithm": "RS256"},
    ]
)
def jwt_handler(request):
    params = request.param
    return JWTHandler(
        private_key=params["private_key"],
        public_key=params["public_key"],
        algorithm=params["algorithm"],
    )


@pytest.fixture
def payload():
    return {"user_id": 123, "username": "test_user"}


class TestJWTHandler:
    def test_encode(self, jwt_handler, payload):
        token = jwt_handler.encode(payload, expire_token=5)
        assert isinstance(token, str)

        token_2 = jwt_handler.encode(payload, expire_token=5)
        assert token == token_2

    def test_decode(self, jwt_handler, payload):
        token = jwt_handler.encode(payload, expire_token=15)
        decoded_token = jwt_handler.decode(token)
        assert decoded_token["user_id"] == payload["user_id"]
        assert decoded_token["username"] == payload["username"]

    def test_decode_invalid_token(self, jwt_handler):
        invalid_token = "this.is.not.a.valid.token"
        with pytest.raises(jwt.DecodeError):
            jwt_handler.decode(invalid_token)

    def test_decode_expired_token(self, jwt_handler, payload):
        token = jwt_handler.encode(payload, expire_token=0)
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt_handler.decode(token)
