from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, Token, UserList, UserPublic, UserSchema
from fast_zero.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)

app = FastAPI()


# response model é o Model de resposta, ou seja,
# o formato da classe de resposta
@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World!'}


# Depends serve como injeção de dependência, ou seja,
# ele toda vez executa o get_session e atribui o retorno dele ao session
@app.post('/users', status_code=HTTPStatus.CREATED, response_model=UserPublic)
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
@app.get('/users', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(limit: int = 10, offset: int = 0, session=Depends(get_session)):
    query = select(User).limit(limit).offset(offset)
    users = session.scalars(query).all()
    return {'users': users}


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def put_users(user_id: int, user: UserSchema, session=Depends(get_session)):
    query = select(User).where(User.id == user_id)

    db_user = session.scalars(query).first()

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    hashed_password = get_password_hash(user.password)
    # Model dump aqui não funciona
    # pq ele acaba identificando como um novo registro (pelo oq testei)

    db_user.email = user.email
    db_user.username = user.username
    db_user.password = hashed_password

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def get_user(user_id: int, session=Depends(get_session)):
    query = select(User).where(User.id == user_id)

    db_user = session.scalars(query).first()

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return db_user


@app.delete(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=Message
)
def delete_user(user_id: int, session=Depends(get_session)):
    query = select(User).where(User.id == user_id)

    db_user = session.scalars(query).first()

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    session.delete(db_user)
    session.commit()

    return {'message': 'User deleted successfully'}


# Depends VAZIO aqui é estranho, mas é só pra dizer ao fastAPI
# que quando não tem nada dentro do Depends, o tipo precisa ser respeitado
@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session=Depends(get_session),
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
