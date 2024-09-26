from datetime import UTC, datetime, timedelta
from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import PyJWTError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User

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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


# esse token serve para caso usuário for fazer uma peração como um delete,
# por exemplo, ele obriga a logar
def get_current_user(
    session: Session = Depends(get_session),
    # não precisa do str, é só pra deixar explico que o retorno
    # vai ser uma string
    token: str = Depends(oauth2_scheme),
):
    credential_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(token, SECRET_KEY, ALGORITHM)
        username: str = payload.get('sub')
        if not username:
            raise credential_exception
    except PyJWTError:
        raise credential_exception
    user = session.scalar(select(User).where(User.username == username))
    if not user:
        raise credential_exception
    return user
