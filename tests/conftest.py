import pytest
from fastapi.testclient import TestClient

from fast_zero.app import app


# fixture para não ter que criar o TestCliente toda vez,
# então passamos ela como parametro para todos os testes
# e ele já vai saber que toda vez que tiver o parametro chamado cliente,
# é para executar essa função, passando o retorno dela pro nosso teste
@pytest.fixture
def client():
    return TestClient(app)
