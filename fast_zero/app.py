from http import HTTPStatus

from fastapi import FastAPI

from fast_zero.schemas import Message, UserPublic, UserSchema

app = FastAPI()


# response model é o Model de resposta, ou seja, o formato da classe de resposta
@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World!'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_users(user: UserSchema):
    return user
