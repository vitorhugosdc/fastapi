from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import Todo, User
from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

T_Session = Annotated['Session', Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


class UserRead(BaseModel):
    id: int
    username: str


class TodoRead(BaseModel):
    username: str
    tittle: str
    description: str
    priority: int
    complete: bool
    user: UserRead


@router.get('')
def read_todos(
    session: T_Session,
    current_user: T_CurrentUser,
    limit: int = 10,
    offset: int = 10,
):
    query = (
        select(Todo)
        .where(current_user.id == Todo.user_id)
        .limit(limit)
        .offset(offset)
    )
    result = session.scalars(query).all()

    return {'todos': result}


class TodoSchema(BaseModel):
    user_id: int
    tittle: str
    description: str
    priority: int
    complete: bool = False


@router.post('', status_code=HTTPStatus.OK, response_model=TodoRead)
def create_todo(
    session: T_Session, current_user: T_CurrentUser, todo: TodoSchema
):
    if current_user.id != todo.user_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, details='User does not exists'
        )
    query = select(User).where(User.id == todo.user_id)
    db_user = session.scalars(query).first()
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, details='User does not exists'
        )
    todo = Todo(
        **todo.model_dump(exclude={'user'})
        # title=todo.tittle,
        # complete=todo.complete,
        # description=todo.description,
        # priority=todo.priority,
        # user_id=current_user.id,
    )
    todo.user = db_user

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
