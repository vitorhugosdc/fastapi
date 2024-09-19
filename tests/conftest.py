import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.models import table_registry


# fixture para não ter que criar o TestCliente toda vez,
# então passamos ela como parametro para todos os testes
# e ele já vai saber que toda vez que tiver o parametro chamado cliente,
# é para executar essa função, passando o retorno dela pro nosso teste
@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
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
