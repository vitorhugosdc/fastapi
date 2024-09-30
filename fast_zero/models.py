# Aqui estão tudo relacionado aos models no banco
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


# TEM que estar em um desses estados
class TodoState(str, Enum):
    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    # todos: Mapped[List['Todo']] = relationship(back_populates='user')


@table_registry.mapped_as_dataclass
class Todo:
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    # priority: Mapped[int]
    state: Mapped[TodoState]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    # sem server_default aqui pois ele já iria inicializar
    # a data de atualização até mesmo na inserção, então deixa só no onupdate
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        init=False,
        onupdate=func.now(),
    )
    # users é o nome da tabela do model User,
    # e users.id tá acessando o id dessa tabela
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    # user: Mapped['User'] = relationship(back_populates='todos')
