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
        x = client.get(base_url)
        assert(x.status_code == 200) or (x.status_code == 301)

    '''
    Test the rest of the urls via HTTP response codes.
    Errs out when one of the response codes isn't 200 (OK)
    '''
    def test_http_site(self, client):
        url_list = ['/announcement', '/calendar']
        base_url = 'http://localhost:8088/'
        for u in url_list:
            x = client.get(u)
            assert(x.status_code == 200) or (x.status_code == 301)

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

        # TODO: Try to log back in as the user
