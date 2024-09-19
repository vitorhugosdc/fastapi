import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry

# fixture para não ter que criar o TestCliente toda vez,
# então passamos ela como parametro para todos os testes
# e ele já vai saber que toda vez que tiver o parametro chamado cliente,
# é para executar essa função, passando o retorno dela pro nosso teste


# agora, passa a ser uma fixture que depende de outra fixture, a session
@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        # isso é especifico do sqlite, onde não pode rodar objetos sqlite em
        # threads diferentes, então settamos para não verificar mais
        connect_args={'check_same_thread': False},
        # não crie várias validaçoes de banco de dados, garanta que tudo vai
        # rodar de forma estática
        poolclass=StaticPool,
    )

    # cria todas as tabelas dos models que estão registrados como
    # @table_registry.mapped_as_dataclass, como o model User por exemplo
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        # yield transforma a Session em um gerador, a fixture vai rodar até o
        # yield
        # e depois vai parar de executar
        # o objeto que foi dado yield (session) é o que vai parar lá dentro do
        #  teste, como parametro session
        # basicamente, até o yield é tudo o que vai ser feito antes do teste,
        # depois dele é o teardown, ou seja, tudo que vc fez, desfaça

        # assistir aula sobre yield, playlist de geradores e corrotinas
        # aula 151 pra frente

        yield session

    # após todos os testes, dropa as tabelas criadas
    table_registry.metadata.drop_all(engine)


# fixture para que se for passado user como parametro, ele vai ter um objeto
# User dentro dele  inserido no banco de dados
# pode ser assim ou fazer mais proximo do rodrigo, ou seja,
# inserindo os usuários via POST no Arrange/Preparação dos testes
# Esse User é um objeto do SQLAlchemy
@pytest.fixture
def user(session):
    user = User(username='johndoe', email='johndoe@me.com', password='secret')
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
