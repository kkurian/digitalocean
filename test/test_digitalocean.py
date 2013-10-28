import pytest


@pytest.fixture
def api():
    import digitalocean
    return digitalocean.DigitalOceanAPI('client_id', 'api_key', False)


def disassemble_path(path):
    parts = path.split('?')
    params = {x.split('=')[0]: x.split('=')[1] for x in parts[1].split('&')}
    return parts, params


def assert_has_credentials(path):
    parts, params = disassemble_path(path)
    assert 'client_id' in params
    assert 'api_key' in params


def strip_credentials(path):
    parts, params = disassemble_path(path)
    del params['client_id']
    del params['api_key']
    params = ['{}={}'.format(k, params[k]) for k in params.keys()]
    return '{}?{}'.format(parts[0], '&'.join(params))


# TODO: Implement test coverage for the case of multiple parameters.
@pytest.mark.parametrize(
    ('api_endpoint', 'params', 'ids', 'output'),
    [
        ('droplets', {}, [], '/droplets?'),
        ('droplets', {}, [], '/droplets?'),
        ('droplets/new', {}, [],'/droplets/new?'),
        ('droplets/reboot', {}, [1], '/droplets/1/reboot?'),
        ('domains/records', {}, [1, 2], '/domains/1/records/2?'),
        ('domains/records/destroy', {}, [1, 2], '/domains/1/records/2/destroy?'),
        ('domains/records/new', {}, [1], '/domains/1/records/new?'),
        ('domains/records/new', {'foo': 'bar'}, [1], '/domains/1/records/new?foo=bar')
    ]
)
def test_resource_path(api, api_endpoint, params, ids, output):
    path = api._make_resource_path(api_endpoint, params, ids)
    assert_has_credentials(path)
    assert output == strip_credentials(path)
