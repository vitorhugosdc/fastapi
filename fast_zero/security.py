from datetime import UTC, datetime, timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import encode
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from fast_zero.database import get_session

pwd_context = PasswordHash.recommended()

SECRET_KEY = 'secret'  # temporário, vai ser ajustado
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 15


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data_payload: dict):
    to_encode = data_payload.copy()

    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


# esse token serve para caso usuário for fazer uma peração como um delete,
# por exemplo, ele obriga a logar
def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
): ...
