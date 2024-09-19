from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_zero.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


def get_session():
    # é tipo try with resources do Java, ele cria a sessão
    # e fecha automaticamente,
    #  por isso não precisa de um session.close()
    # basicamente, essa função vai executar até o yield,
    # ai vai voltar lá nas funções que o chamaram,
    # e após executar elas, retorna para cá e finaliza a sessão automaticamente
    with Session(engine) as session:
        yield session
