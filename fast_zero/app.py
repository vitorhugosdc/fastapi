from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserDB, UserList, UserPublic, UserSchema

app = FastAPI()

# banco de dados fake, por enquanto
database = []


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
        password=user.password,
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
def put_users(user_id: int, user: UserSchema):
    if user_id - 1 > len(database) or database[user_id - 1] is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    user_with_id = UserDB(**user.model_dump(), id=user_id)

    database[user_id - 1] = user_with_id

    return user_with_id


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def get_user(user_id: int):
    if user_id - 1 > len(database) or database[user_id - 1] is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return database[user_id - 1]


@app.delete(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=Message
)
def delete_user(user_id: int):
    if user_id - 1 > len(database) or database[user_id - 1] is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )
    database.pop(user_id - 1)
    return {'message': 'User deleted successfully'}
