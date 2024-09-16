from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


# é o tipo de dado que representa o usuário, sendo também o tipo de dado que
# sera recebido no POST, ou seja, é um modelo de contrato de ENTRADA
class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


# é o mesmo conceito de um DTO, utilizado para não retornar a senha na resposta
# ou seja, é um modelo de contrato de SAÍDA
class UserPublic(BaseModel):
    username: str
    email: EmailStr
