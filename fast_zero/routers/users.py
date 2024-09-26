from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema
from fast_zero.security import get_current_user, get_password_hash

# prefix é pra ser sempre /users antes, por exemplo, tipo do Spring
# tags é pra lá na documentação ele organizar
# as coisas que são do mesmo dominio
router = APIRouter(prefix='/users', tags=['users'])


# Depends serve como injeção de dependência, ou seja,
# ele toda vez executa o get_session e atribui o retorno dele ao session
@router.post('', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_users(user: UserSchema, session=Depends(get_session)):
    querry = select(User).where(
        (User.username == user.username) | (User.email == user.email)
    )

    db_user = session.scalar(querry)

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exists',
            )
        # acho que não precisa do elif, somente if
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )

    hashed_password = get_password_hash(user.password)

    # poderia usar o model dump
    # meio que ele instancia o User recebendo todos parametros em forma de
    # dicionario (chave,valor) do UserSchema
    # ai como User gera automaticamente o id e o created_by, não precisamos
    #  passar o parametro
    # também daria para modifica algum parametro na instanciação,
    # como por exemplo:
    # db_user = User(**user.model_dump(), email='user@me.com'),
    # instanciado email como o valor passado, e não do model_dump()
    # como seria então:
    # db_user = User(**user.model_dump())

    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


# limit = 10 e offset = 0 são valores padrão,
# ou seja, se não forem passados, vão ser esses valores
@router.get('', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    limit: int = 10,
    offset: int = 0,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    query = select(User).limit(limit).offset(offset)
    users = session.scalars(query).all()
    return {'users': users}


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    # Model dump aqui não funciona
    # pq ele acaba identificando como um novo registro (pelo oq testei)

    current_user.email = user.email
    current_user.username = user.username
    current_user.password = get_password_hash(user.password)

    session.commit()
    session.refresh(current_user)

    return current_user


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def get_user(
    user_id: int,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    return current_user


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(
    user_id: int,
    # só pra deixar mais explicito, tanto faz, outra maneira de fazer
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted successfully'}
