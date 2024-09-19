from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.models import User


def test_create_user_db(session: Session):
    user = User(username='johndoe', email='johndoe@me.com', password='secret')

    session.add(user)
    session.commit()
    # session.refresh(user)

    result = session.scalar(select(User).where(User.email == 'johndoe@me.com'))

    assert result.username == 'johndoe'
