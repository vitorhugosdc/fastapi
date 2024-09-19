from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_read_root_must_return_ok_and_hello_world(client):
    # client = TestClient(app)  # Arrange

    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # assert
    assert response.json() == {'message': 'Hello World!'}
    response.json().get('message') == 'Hello World!'


def test_create_user(client):
    # client = TestClient(app)

    # arrange
    response = client.post(
        '/users',
        json={
            'username': 'johndoe',
            'email': 'johndoe@me.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'johndoe',
        'email': 'johndoe@me.com',
    }


def test_read_users(client):
    user1 = client.post(
        '/users',
        json={
            'username': 'johndoe',
            'email': 'johndoe@me.com',
            'password': 'secret',
        },
    )

    user2 = client.post(
        '/users',
        json={
            'username': 'johndoe2',
            'email': 'johndoe2@me.com',
            'password': 'secret2',
        },
    )

    user1 = user1.json()
    user2 = user2.json()

    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': user1.get('id'),
                'username': user1.get('username'),
                'email': user1.get('email'),
            },
            {
                'id': user2.get('id'),
                'username': user2.get('username'),
                'email': user2.get('email'),
            },
        ]
    }


# aqui é só pra testar como funciona testar com um usuário
# dentro do banco de dados
# inserido pela fixture, e não pelo post ou com Factorys
# O user que chega, AINDA é um objeto do SQLAlchemy
def test_read_users_with_user(client, user):
    # converte uma classe do SQLAlchemy para um schema do pydantic
    # basicamente ele vê se o objeto do SQLAlchemy (user) pode ser convertido
    # para um UserPublic, o que vai dar erro pois ele não conhece esse objeto
    # e o fato dele não conhecer esse objeto, faz com oq a gente tenha que lá
    # no schema de UserPublic(pasta schemas) e configurar com o ConfigDict
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_put_users(client, user):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'vitor',
            'email': 'vitor@me.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }


# Como para encontrar um user pelo id, ele precisa existir,
# recebemos o user da fixture, que é um user que já está no banco de dados
def test_get_user(client, user):
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }


def test_get_user_not_found(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == {'detail': 'User not found'}


# não vai passar por enquanto pois o banco de dados é fake
# e não reseta antes de cada teste
def test_put_users_not_found(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'vitor',
            'email': 'vitor@me.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


# Não precisa inserir um usuário no banco de dados utilizando POST
# no Arrange do test (mas pode), pois ao receber user da fixture
# esse usuário já está no banco de dados
def test_delete_user(client, user):
    response = client.delete(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {
        'message': 'User deleted successfully',
    }


# Como aqui não está sendo recebido o user gerado pela fixture,
# não tem nenhum usuário no banco de dados
def test_delete_user_not_found(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == {'detail': 'User not found'}
