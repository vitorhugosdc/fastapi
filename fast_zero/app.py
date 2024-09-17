from http import HTTPStatus

from fastapi import FastAPI

from fast_zero.schemas import Message, UserDB, UserPublic, UserSchema

app = FastAPI()

# banco de dados fake, por enquanto
database = []


# response model é o Model de resposta, ou seja,
# o formato da classe de resposta
@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World!'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_users(user: UserSchema):
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)

    # model_dump tira do formato do Pydantic e cria um dicionário
    database.append(user_with_id)

    return user_with_id
