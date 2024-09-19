from http import HTTPStatus

from fast_zero.schemas import UserPublic

database = []


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
def test_read_users_with_user(client, user):
    # converte uma classe do SQLAlchemy para um schema do pydantic
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_put_users(client):
    response = client.put(
        '/users/2',
        json={
            'username': 'vitor',
            'email': 'vitor@me.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {
        'id': 2,
        'username': 'vitor',
        'email': 'vitor@me.com',
    }


def test_get_user(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {
        'id': 1,
        'username': 'johndoe',
        'email': 'johndoe@me.com',
    }


def test_get_user_not_found(client):
    response = client.get('/users/300')

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == {'detail': 'User not found'}


# não vai passar por enquanto pois o banco de dados é fake
# e não reseta antes de cada teste
def test_put_users_not_found(client):
    response = client.put(
        '/users/300',
        json={
            'username': 'vitor',
            'email': 'vitor@me.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {
        'message': 'User deleted successfully',
    }


def test_delete_user_not_found(client):
    response = client.delete('/users/300')

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == {'detail': 'User not found'}
