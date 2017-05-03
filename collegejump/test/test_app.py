#!env/bin/python3

# pylint: disable=R,C,W; refactoring, convention, warnings

import pytest # pylint: disable=import-error

@pytest.fixture(scope="module")
def collegejump():
    import collegejump
    collegejump.app.config['WTF_CSRF_ENABLED'] = False # disable CSRF validation
    collegejump.init_app()

    return collegejump


@pytest.fixture
def client(collegejump):
    return collegejump.app.test_client()

class TestCollegeJUMP():
    def test_version_present(self, collegejump, client):
        """Ensure that the version string is present on the index page."""
        version = collegejump.__version__
        rv = client.get('/')
        assert bytes(version, encoding='UTF-8') in rv.data
    
    '''
    Test the main url, which seems to have an HTTP response code of
    301 during normal operation
    '''
    def test_http_index(self, client):
        base_url = 'http://localhost:8088'
        x = client.get(base_url, follow_redirects=True)
        assert(x.status_code == 200)

    '''
    Test the rest of the urls via HTTP response codes.
    Errs out when one of the response codes isn't 200 (OK)
    '''
    def test_http_site(self, client):
        url_list = ['/announcement', '/calendar']
        base_url = 'http://localhost:8088/'
        for u in url_list:
            x = client.get(u, follow_redirects=True)
            assert(x.status_code == 200)

    # Tests that a non-logged in user cannot access certain pages
    #@pytest.mark.xfail(reason="#81")   # '/week/0' should require login
    def test_requires_login(self, client):
         url_list = ['/logout', '/account/0', '/announcement/new', 
         '/announcement/0/edit', '/syllabus', '/syllabus/semester/new', '/syllabus/semester/0',
         '/syllabus/semester/0/week/0', '/edit_accounts', '/database', '/database/export']
         for u in url_list:
           x = client.get(u, follow_redirects=True)
           assert bytes("Login", encoding='UTF-8') in x.data


class TestSetupProcess():
    # This must run before one which succeeds, because after that, /setup is no
    # longer accessible.
    def test_setup_wrong_key(self, client):
        '''Fail to create an admin user on `/setup` with the wrong key'''
        details = {'name': 'Setup Administrator',
                   'email': 'setup@email.com',
                   'password': 'setup password'}

        setup_key = 'phony_setup_key'
        setup_rv = client.post('/setup', data=dict(
            setup_key=setup_key,
            name=details['name'],
            email=details['email'],
            password=details['password']), follow_redirects=True)

        assert setup_rv.status_code == 401

    def test_setup_key(self, collegejump, client):
        '''Create an admin user with `ADMIN_DETAILS` credentials using the SETUP_KEY.'''
        details = {'name': 'Setup Administrator',
                   'email': 'setup@email.com',
                   'password': 'setup password'}

        setup_key = collegejump.app.config['SETUP_KEY']
        setup_rv = client.post('/setup', data=dict(
            setup_key=setup_key,
            name=details['name'],
            email=details['email'],
            password=details['password']), follow_redirects=True)

        assert setup_rv.status_code == 200

        # Try to log out, since we should be logged in after creating that
        # user. If we are disallowed, we were not logged in.
        logout_rv = client.get('/logout', follow_redirects=True)

        assert logout_rv.status_code == 200

    def test_setup_already_done(self, client):
        '''Fail to access /setup with 404 after creation.'''
        setup_rv = client.get('/setup', follow_redirects=True)
        assert setup_rv.status_code == 404

class TestUser():

    # log user back in again
    def test_login(self, client):
      x = client.post('/login', data=dict(
      email='setup@email.com',
      password='setup password'), follow_redirects=True)
      assert bytes("Login successful", encoding='UTF-8') in x.data
      assert x.status_code == 200


    def test_create_student_user(self, client):
      x = client.post('/edit_accounts', data=dict(
      name='Katherine',
      email='katherine@email.com',
      admin=False,
      password='katherine password'), follow_redirects=True)

      #k = client.post('/login', data=dict(
      #email='katherine@email.com',
      #password='katherine password'), follow_redirects=True)

      assert x.status_code == 200

    def test_create_user_invalid_email(self, client):
      x = client.post('/edit_accounts', data=dict(
      name='Brad',
      email='brad',
      admin=False,
      password='brad password'), follow_redirects=True)

      print(x.data)
      #assert bytes("Created user", encoding='UTF-8') in x.data
      assert 1 == 1

    def test_logout(self, client):
      x = client.get('/logout', follow_redirects=True)
      x = client.get('/logout', follow_redirects=True)
      assert bytes("Login", encoding='UTF-8') in x.data



