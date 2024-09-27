from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Token
from fast_zero.security import create_access_token, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])
T_Session = Annotated['Session', Depends(get_session)]
T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=Token)
def login_for_access_token(
    session: T_Session,
    # Depends VAZIO aqui é estranho, mas é só pra dizer ao fastAPI
    # que quando não tem nada dentro do Depends, o tipo precisa ser respeitado
    form_data: T_OAuth2Form,
):
    user = session.scalar(
        select(User).where(User.username == form_data.username)
    )
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password',
            # headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token = create_access_token(data_payload={'sub': user.username})

    return {'access_token': access_token, 'token_type': 'Bearer'}
