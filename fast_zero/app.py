from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from fast_zero.schemas import Message, UserDB, UserList, UserPublic, UserSchema

app = FastAPI()

# banco de dados fake, por enquanto
database = []


# response model é o Model de resposta, ou seja,
# o formato da classe de resposta
@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World!'}


@app.post('/users', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_users(user: UserSchema):
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)

    # model_dump tira do formato do Pydantic e cria um dicionário
    database.append(user_with_id)

    return user_with_id


@app.get('/users', status_code=HTTPStatus.OK, response_model=UserList)
def read_users():
    return {'users': database}


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
