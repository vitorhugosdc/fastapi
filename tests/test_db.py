from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_zero.models import User, table_registry


def test_create_user_db():
    engine = create_engine(
        'sqlite:///:memory:',
    )

    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(
            username='johndoe', email='johndoe@me.com', password='secret'
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        assert user.id == 1
