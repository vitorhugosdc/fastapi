from http import HTTPStatus


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
        # 'title': 'Buy milk',
        # 'description': 'Need to buy milk',
        # 'state': 'draft',
    }
