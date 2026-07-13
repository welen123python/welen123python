from app.auth import get_password_hash, verify_password, create_access_token
from jose import jwt
from app.config import settings

def test_password_hashing():
    password = "secure_arbitrage_123!"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_jwt_generation_and_verification():
    username = "arbitrageur"
    token = create_access_token(subject=username)

    assert token is not None
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == username
