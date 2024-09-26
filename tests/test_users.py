from http import HTTPStatus

from fast_zero.schemas import UserPublic
from fast_zero.security import get_password_hash


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


def test_create_username_already_exists(client):
    # arrange
    client.post(
        '/users',
        json={
            'username': 'johndoe',
            'email': 'johndoe@me.com',
            'password': 'secret',
        },
    )

    # act
    response = client.post(
        '/users',
        json={
            'username': 'johndoe',
            'email': 'johndoe2@me.com',
            'password': 'secret',
        },
    )

    # assert
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}


def test_create_username_already_exists_second_method(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'johndoe',
            'email': 'johndoe2@me.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}


def test_create_email_already_exists(client):
    # client = TestClient(app)

    # arrange
    client.post(
        '/users',
        json={
            'username': 'johndoe',
            'email': 'johndoe@me.com',
            'password': 'secret',
        },
    )

    response = client.post(
        '/users',
        json={
            'username': 'johndoe2',
            'email': 'johndoe@me.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists'}


def test_read_users(client, user, token):
    # user1 = client.post(
    #     '/users',
    #     json={
    #         'username': 'johndoe',
    #         'email': 'johndoe@me.com',
    #         'password': get_password_hash('secret'),
    #     },
    # )

    user2 = client.post(
        '/users',
        json={
            'username': 'johndoe2',
            'email': 'johndoe2@me.com',
            'password': get_password_hash('secret'),
        },
    )

    # user1 = user1.json()
    user2 = user2.json()

    response = client.get(
        '/users', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
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
def test_read_users_with_user(client, user, token):
    # converte uma classe do SQLAlchemy para um schema do pydantic
    # basicamente ele vê se o objeto do SQLAlchemy (user) pode ser convertido
    # para um UserPublic, o que vai dar erro pois ele não conhece esse objeto
    # e o fato dele não conhecer esse objeto, faz com oq a gente tenha que lá
    # no schema de UserPublic(pasta schemas) e configurar com o ConfigDict
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get(
        '/users', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_users(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'vitor',
            'email': 'vitor@me.com',
            'password': 'secret',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }


# Como para encontrar um user pelo id, ele precisa existir,
# recebemos o user da fixture, que é um user que já está no banco de dados
def test_get_user(client, user, token):
    response = client.get(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }


def test_get_user_not_found(client, token):
    response = client.get(
        '/users/2', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    assert response.json() == {'detail': 'Not enough permissions'}


# não vai passar por enquanto pois o banco de dados é fake
# e não reseta antes de cada teste
def test_put_users_not_found(client, token):
    response = client.put(
        '/users/2',
        json={
            'username': 'vitor',
            'email': 'vitor@me.com',
            'password': 'secret',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    assert response.json() == {'detail': 'Not enough permissions'}


# Não precisa inserir um usuário no banco de dados utilizando POST
# no Arrange do test (mas pode), pois ao receber user da fixture
# esse usuário já está no banco de dados
# também...
# Como a gente precisa do token,
# sempre o usuário do token vai estar inserido no banco, ou seja,
# id 1 sempre vai existir, então o user recebido é o mesmo user do token
def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {
        'message': 'User deleted successfully',
    }


# Como a gente precisa do token,
# sempre o usuário do token vai estar inserido no banco, ou seja,
# id 1 sempre vai existir
def test_delete_user_not_found(client, token):
    response = client.delete(
        '/users/2', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    assert response.json() == {'detail': 'Not enough permissions'}
