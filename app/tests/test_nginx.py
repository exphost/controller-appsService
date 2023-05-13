USER="eyJpc3MiOiAiaHR0cHM6Ly9hdXRoLmdhdGV3YXktMzktZGV2LXBhc3MtdXNlci0wNWxzamMuY2kuZXhwaG9zdC5wbC9kZXgiLCAic3ViIjogIkNnZDBaWE4wTFhCeUVnUnNaR0Z3IiwgImF1ZCI6ICJleHBob3N0LWNvbnRyb2xsZXIiLCAiZXhwIjogMTY1MjE4MDM1MywgImlhdCI6IDE2NTIwOTM5NTMsICJhdF9oYXNoIjogIjc1a0NUUkRxTFFMU19XWjgyVUtXZGciLCAiZW1haWwiOiAidGVzdC1wckBtYWlsLnJ1IiwgImVtYWlsX3ZlcmlmaWVkIjogdHJ1ZSwgImdyb3VwcyI6IFsidGVzdC11c2VyIiwgInRlc3Qtb3JnIl0sICJuYW1lIjogInRlc3QtdXNlciJ9" # noqa


def test_nginx_add(client, app):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'app_name': 'app1',
              'name': 'add-app1'},
        headers={'X-User-Full': USER})
    assert response.status_code == 201

    component = app.dao.get_component(
        org="test-org",
        app="app1",
        component="add-app1")
    assert component == {
        'name': 'nginx',
        'releaseName': 'add-app1',
        'repo': 'https//gitlab.exphost.pl/charts',
        'version': '10.0.1',
        'valuesInline': {
            '_type': 'nginx',
            'ingress': {
                'enabled': True,
                'hostname': 'add-app1.test-org.users.example.com',
                'annotations': {
                    'cert-manager.io/cluster-issuer': 'acme-issuer',
                },
                'tls': True,
                'certManager': True,
            },
            'service': {
                'type': 'ClusterIP',
            },
        },
    }


def test_nginx_add_non_existing_app(client, app):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'app_name': 'app10',
              'name': 'add-app1'},
        headers={'X-User-Full': USER})
    assert response.status_code == 404


def test_nginx_add_static_page(client, app):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'app_name': 'app1',
              'name': 'add-app2',
              'git': {'repo': 'https://github.com/example/example.git',
                      'branch': 'devel'},
              'fqdns': ['example.example.com', 'www2.example.ru']},
        headers={'X-User-Full': USER})
    assert response.status_code == 201

    component = app.dao.get_component(
        org="test-org",
        app="app1",
        component="add-app2")
    assert component['valuesInline'] == {
        '_type': 'nginx',
        'ingress': {
            'enabled': True,
            'hostname': 'add-app2.test-org.users.example.com',
            'annotations': {
                'cert-manager.io/cluster-issuer': 'acme-issuer',
            },
            'extraHosts': [
                {
                    'name': 'example.example.com',
                    'path': '/',
                },
                {
                    'name': 'www2.example.ru',
                    'path': '/',
                },
            ],
            'tls': True,
            'certManager': True,
        },
        'service': {
            'type': 'ClusterIP',
        },
        'cloneStaticSiteFromGit': {
            'enabled': True,
            'repository': 'https://github.com/example/example.git',
            'branch': 'devel',
        },
    }


def test_nginx_add_static_page_default_branch(client, app):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'app_name': 'app1',
              'name': 'add-app',
              'git': {'repo': 'https://github.com/example/example.git'},
              'fqdns': ['example.example.com']},
        headers={'X-User-Full': USER})
    assert response.status_code == 201

    component = app.dao.get_component(
        org="test-org",
        app="app1",
        component="add-app")
    assert component['valuesInline'] == {
        '_type': 'nginx',
        'ingress': {
            'enabled': True,
            'hostname': 'add-app.test-org.users.example.com',
            'annotations': {
                'cert-manager.io/cluster-issuer': 'acme-issuer',
            },
            'extraHosts': [
                {
                    'name': 'example.example.com',
                    'path': '/',
                },
            ],
            'tls': True,
            'certManager': True,
        },
        'service': {
            'type': 'ClusterIP',
        },
        'cloneStaticSiteFromGit': {
            'enabled': True,
            'repository': 'https://github.com/example/example.git',
            'branch': 'master',
        },
    }


def test_nginx_add_static_page_missing_repo(client, app):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'app_name': 'app1',
              'name': 'add-app',
              'git': {'branch': 'devel'},
              'fqdns': ['example.example.com']},
        headers={'X-User-Full': USER})
    assert response.status_code == 400


def test_nginx_add_duplicate(client):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'app_name': 'app1',
              'name': 'add-app'},
        headers={'X-User-Full': USER})
    assert response.status_code == 201
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'app_name': 'app1',
              'name': 'add-app'},
        headers={'X-User-Full': USER})
    assert response.status_code == 409


def test_nginx_add_missing_name(client):
    response = client.post(
        '/nginx/',
        json={'name': 'test-app'})
    assert response.status_code == 400


def test_nginx_add_missing_app_name(client):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'app_name': 'app1',
              'name': 'add-app'},
        headers={'X-User-Full': USER})
    assert response.status_code == 201


def test_nginx_add_not_logged(client):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'app_name': 'app1',
              'name': 'test-app'})
    assert response.status_code == 401


def test_nginx_list(client, app):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'app_name': 'app1',
              'name': 'add-app2',
              'git': {'repo': 'https://github.com/example/example.git',
                      'branch': 'devel'},
              'fqdns': ['example.example.com', 'www2.example.ru']},
        headers={'X-User-Full': USER})
    assert response.status_code == 201
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'app_name': 'app1',
              'name': 'add-app1'},
        headers={'X-User-Full': USER})
    assert response.status_code == 201

    response = client.get(
        '/nginx/?org=test-org&app_name=app1',
        headers={'X-User-Full': USER})
    assert response.status_code == 200
    assert 'nginx' in response.json
    assert len(response.json['nginx']) == 2
    apps = sorted(response.json['nginx'], key=lambda x: x['name'])
    print(apps)
    assert apps[0]['name'] == "add-app1"
    assert apps[1]['name'] == "add-app2"
    assert 'git' not in apps[0]
    assert apps[1]['git']['repo'] == "https://github.com/example/example.git"
    assert apps[1]['git']['branch'] == "devel"
    assert "www2.example.ru" in apps[1]['fqdns']
    assert "example.example.com" in apps[1]['fqdns']
    assert "add-app2.test-org.users.example.com" in apps[1]['fqdns']


def test_nginx_list_empty_app_name(client):
    response = client.get(
        '/nginx/?org=test-org&app_name=app_not_exist',
        headers={'X-User-Full': USER})
    assert response.status_code == 404


def test_nginx_list_no_org(client):
    response = client.get(
        '/nginx/',
        headers={'X-User-Full': USER})
    assert response.status_code == 400


def test_nginx_list_no_app(client):
    response = client.get(
        '/nginx/?org=test-org',
        headers={'X-User-Full': USER})
    assert response.status_code == 400


def test_nginx_list_not_logged(client):
    response = client.get(
        '/nginx/?org=test-org')
    assert response.status_code == 401


def test_nginx_add_wrong_org(client):
    response = client.post(
        '/nginx/',
        json={'org': 'another-org',
              'app_name': 'app1',
              'name': 'add-app'},
        headers={'X-User-Full': USER})
    assert response.status_code == 403


def test_nginx_list_wrong_org(client):
    response = client.get(
        '/nginx/?org=another-org',
        headers={'X-User-Full': USER})
    assert response.status_code == 403
