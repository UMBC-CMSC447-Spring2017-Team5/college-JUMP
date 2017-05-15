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

    # Ensure that the version string is present on the index page
    def test_version_present(self, collegejump, client):
        version = collegejump.__version__
        rv = client.get('/')
        assert bytes(version, encoding='UTF-8') in rv.data

    # Test the main url
    def test_http_index(self, client):
        base_url = '/'
        x = client.get(base_url, follow_redirects=True)
        assert(x.status_code == 200)

    # Test other urls not requiring login via HTTP response codes.
    def test_http_site(self, client):
        url_list = ['/announcement', '/calendar']
        for u in url_list:
            x = client.get(u, follow_redirects=True)
            assert(x.status_code == 200)

    # Tests that a non-logged in user cannot access certain pages
    def test_requires_login(self, client):
         url_list = ['/logout', '/account/1', '/announcement/new', 
         '/announcement/1/edit', '/syllabus', '/syllabus/semester/1',
         '/syllabus/semester/1/week/1', '/account/all', '/database', '/database/export',
         '/submission/1', '/semester/1/week/1', '/document/1']
         for u in url_list:
           x = client.get(u, follow_redirects=True)
           assert bytes("Login", encoding='UTF-8') in x.data


class TestSetupProcess():

    # Test setup key
    @pytest.mark.xfail(reason="#81")
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

    # Test valid setup key
    @pytest.mark.xfail(reason="#81")
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

    # Test setup worked
    @pytest.mark.xfail(reason="#81")
    def test_setup_already_done(self, client):
        '''Fail to access /setup with 404 after creation.'''
        setup_rv = client.get('/setup', follow_redirects=True)
        assert setup_rv.status_code == 404

class TestUser():

    # log user back in again
    @pytest.mark.xfail(reason="#81")
    def test_login(self, client):
      x = client.post('/login', data=dict(
      email='setup@email.com',
      password='setup password'), follow_redirects=True)
      assert x.status_code == 200

    # Test creation of valid student user
    @pytest.mark.xfail(reason="#81")
    def test_create_student_user(self, client):
      x = client.post('/account/all', data=dict(
      name='Katherine',
      email='katherine@email.com',
      admin=False,
      password='katherine password'), follow_redirects=True)

      assert x.status_code == 200

    # Test logout successful
    def test_logout(self, client):
      x = client.get('/logout', follow_redirects=True)
      x = client.get('/logout', follow_redirects=True)
      assert bytes("Login", encoding='UTF-8') in x.data



