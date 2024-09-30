from http import HTTPStatus

from tests.conftest import TodoFactory


def test_create_todo(client, token):
    response = client.post(
        '/todos',
        json={
            'title': 'Buy milk',
            'description': 'Need to buy milk',
            'state': 'draft',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'Buy milk',
        'description': 'Need to buy milk',
        'state': 'draft',
    }


def test_list_todos_should_return_5_todos(session, client, user, token):
    expected_todos = 5
    # inserindo 5 objetos no banco de uma vez só
    session.bulk_save_objects(
        TodoFactory.create_batch(expected_todos, user_id=user.id)
    )
    session.commit()

    response = client.get(
        '/todos', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    # assert len(response.json()) == expected_todos
    assert len(response.json()['todos']) == expected_todos
