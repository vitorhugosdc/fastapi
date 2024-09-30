from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import Todo, TodoState, User
from fast_zero.schemas import Message
from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

T_Session = Annotated['Session', Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState


class TodoPublic(TodoSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ListTodoPublic(BaseModel):
    todos: list[TodoPublic]


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None


@router.get('', status_code=HTTPStatus.OK, response_model=ListTodoPublic)
# talvez pra evitar tantos parâmetros, criar uma classe que represente eles
# e acessar pela classe?
def read_todos(  # noqa
    session: T_Session,
    current_user: T_CurrentUser,
    limit: int = 10,
    offset: int = 0,
    # str | None definiria que o title poderia ser str ou None,
    # mas o parâmetro deveria ser recebido obrigatoriamente
    # Agora, ao utilizar None = None dizemos que
    # se nada for informado, o valor padrão será None,
    # ou seja, não será obrigatório enviar o parâmetro
    title: str | None = None,
    state: TodoState | None = None,
    description: str | None = None,
):
    # inicializa a query de forma geral
    query = (
        select(Todo)
        .where(Todo.user_id == current_user.id)
        .limit(limit)
        .offset(offset)
    )

    # vai adicionando filtros na query
    if title:
        # contais é o %LIKE%
        query = query.filter(Todo.title.contains(title))
    if state:
        # apenas uma maneira de fazer oq foi feito acima,
        # poderia utilizar só == mesmo,
        # seja com filter ou com where
        # query = query.filter(Todo.state == state)
        # query = query.where(Todo.state == state)
        query = query.filter(Todo.state.in_([state]))
    if description:
        # apenas uma maneira de fazer oq foi feito no title acima,
        # poderia ser f'{description}%' ou f'%{description}' também
        # query = query.filter(Todo.description.like(f'%{description}%'))
        query = query.where(Todo.description.like(f'%{description}%'))

    todos = session.scalars(query).all()

    return {'todos': todos}


@router.post('', status_code=HTTPStatus.CREATED, response_model=TodoPublic)
def create_todo(
    session: T_Session, current_user: T_CurrentUser, todo: TodoSchema
):
    todo = Todo(
        **todo.model_dump(exclude={'user_id'}),
        user_id=current_user.id,
        # title=todo.tittle,
        # complete=todo.complete,
        # description=todo.description,
        # priority=todo.priority,
        # user_id=current_user.id,
    )
    # todo.user = db_user

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.delete('/{todo_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_todo(session: T_Session, current_user: T_CurrentUser, todo_id: int):
    # todo = session.get(Todo, todo_id)

    # primeira maneira (que eu tive a ideia)
    # todo = session.scalars(select(Todo).where(Todo.id == todo_id)).first()

    # if current_user.id != todo.user_id:
    #     raise HTTPException(
    #         status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
    #     )

    # segunda maneira, ensinada no curso
    todo = session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Todo not found'
        )

    session.delete(todo)
    session.commit()
    return {'message': 'Todo deleted successfully'}


@router.patch(
    '/{todo_id}', status_code=HTTPStatus.OK, response_model=TodoPublic
)
def patch_todo(
    session: T_Session,
    current_user: T_CurrentUser,
    todo_id: int,
    todo: TodoUpdate,
):
    db_todo = session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Todo not found'
        )

    # rever a explicação do model_dump, que eu me lembre ele transforma
    # um objeto em forma de dicionário, chave e valor,
    # ou seja, ele cria uma representação do objeto em forma de dicionário
    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo
