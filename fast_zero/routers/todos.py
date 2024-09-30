from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import Todo, TodoState, User
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


@router.get('', status_code=HTTPStatus.OK, response_model=ListTodoPublic)
# talvez pra evitar tantos parâmetros, criar uma classe que represente eles
# e acessar pela classe?
def read_todos(  # noqa
    session: T_Session,
    current_user: T_CurrentUser,
    limit: int = 10,
    offset: int = 0,
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
