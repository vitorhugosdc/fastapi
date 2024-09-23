from jwt import decode

from fast_zero.security import ALGORITHM, SECRET_KEY, create_access_token


def test_jwt():
    data = {'sub': 'test'}
    token = create_access_token(data)

    result = decode(token, SECRET_KEY, ALGORITHM)

    assert result['sub'] == data['sub']
    assert result['exp']
