from http import HTTPStatus

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
            'username': 'johndoe',
            'email': 'johndoe@me.com',
            'password': 'secret',
        },
    )

    user1 = user1.json()
    user2 = user2.json()

    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'johndoe',
                'email': 'johndoe@me.com',
            },
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
