from http import HTTPStatus

from fast_zero.models import TodoState
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
    # o retorno do get é chave todos e valor uma lista de todos,
    # por isso estamos acessando o .json() dessa maneira,
    # estamos acessando a chave todos
    # e vendo se o tamanho de seus valores é expected_todos
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_pagination_should_return_2_todos(
    session, client, user, token
):
    all_todos = 5
    expected_todos = 2
    session.bulk_save_objects(
        TodoFactory.create_batch(all_todos, user_id=user.id)
    )
    session.commit()

    response = client.get(
        '/todos?offset=1&limit=2', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_by_tittle(session, client, user, token):
    all_todos = 5
    expected_todos = 1
    session.bulk_save_objects(
        TodoFactory.create_batch(all_todos, user_id=user.id)
    )

    todo = TodoFactory(title='buy', user_id=user.id)
    session.add(todo)

    # poderia ser só essa linha
    # session.add(TodoFactory(title='buy', user_id=user.id))

    session.commit()

    response = client.get(
        '/todos?title=buy',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos
    # 2 maneiras de fazer
    assert response.json()['todos'][0]['title'] == todo.title
    assert response.json()['todos'][0]['title'] == 'buy'


def test_list_todos_by_description(session, client, user, token):
    all_todos = 5
    expected_todos = 2
    session.bulk_save_objects(
        TodoFactory.create_batch(all_todos, user_id=user.id)
    )

    todo = TodoFactory(description='blabla', user_id=user.id)
    todo2 = TodoFactory(description='bla', user_id=user.id)
    # session.add(todo)
    # session.add(todo2)

    session.bulk_save_objects([todo, todo2])

    # poderia ser só essa linha
    # session.add(TodoFactory(title='buy', user_id=user.id))

    session.commit()

    response = client.get(
        '/todos?description=bla',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos
    # 2 maneiras de fazer, basicamente é a mesma coisa
    assert response.json()['todos'][0]['description'] == todo.description
    assert response.json()['todos'][0]['description'] == 'blabla'
    # 2 maneiras de fazer, basicamente é a mesma coisa
    assert response.json()['todos'][1]['description'] == todo2.description
    assert response.json()['todos'][1]['description'] == 'bla'


def test_list_todos_by_state(session, client, user, token):
    all_todos = 5
    expected_todos = 1
    session.bulk_save_objects(
        TodoFactory.create_batch(
            all_todos, user_id=user.id, state=TodoState.done
        )
    )

    todo = TodoFactory(state='done', user_id=user.id)
    todo2 = TodoFactory(state='draft', user_id=user.id)

    # session.add(todo)
    # session.add(todo2)

    # ou salva tudo junto igual abaixo
    session.bulk_save_objects([todo, todo2])

    # poderia ser só essa linha
    # session.add(TodoFactory(title='buy', user_id=user.id))

    session.commit()

    response = client.get(
        '/todos?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos
    # 2 maneiras de fazer, basicamente é a mesma coisa
    assert response.json()['todos'][0]['state'] == todo2.state
    assert response.json()['todos'][0]['state'] == 'draft'


# falta testar combinações de filtros


def test_delete_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.delete(
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Todo deleted successfully'}


def test_delete_todo_error(session, client, user, other_user, token):
    todo = TodoFactory(user_id=user.id)
    todo2 = TodoFactory(user_id=other_user.id)
    session.bulk_save_objects([todo, todo2])
    session.commit()

    # tentando deletar do user uma todo do other_user, com o token do user
    # poderia ser só todo.id+1, usei outro user pra ficar mais enfeitado
    response = client.delete(
        f'/todos/{other_user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}


def test_patch_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        # poderia mandar um json vazio também,
        # uma vez que no schema do update, ele aceita até tudo nulo,
        # então seria um update que não altera nada
        json={'title': 'new title'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    # acessando a chave title na resposta
    assert response.json()['title'] == 'new title'


def test_patch_todo_error(client, token):
    response = client.patch(
        '/todos/1',
        json={'title': 'new title'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}
