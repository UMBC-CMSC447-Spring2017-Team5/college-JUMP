#!env/bin/python3

# pylint: disable=R,C,W; refactoring, convention, warnings

import pytest # pylint: disable=import-error

@pytest.fixture(scope="module")
def collegejump():
    import collegejump
    return collegejump


@pytest.fixture(scope="module")
def app():
    import collegejump
    test_app = collegejump.app.test_client()
    collegejump.init_app()
    return test_app


class TestCollegeJUMP():
    def test_version_present(self, collegejump, app):
        """Ensure that the version string is present on the index page."""
        version = collegejump.__version__
        rv = app.get('/')
        assert bytes(version, encoding='UTF-8') in rv.data
    
    '''
    Test the main url, which seems to have an HTTP response code of
    301 during normal operation
    '''

    def test_http_index(self, collegejump, app):
        base_url = 'http://localhost:8088'
        x = app.get(base_url)
        assert(x.status_code == 200) or (x.status_code == 301)

    '''
    Test the rest of the urls via HTTP response codes.
    Errs out when one of the response codes isn't 200 (OK)
    '''
    def test_http_site(self, collegejump, app):
        url_list = ['/announcement', '/calendar']
        base_url = 'http://localhost:8088/'
        for u in url_list:
            x = app.get(u)
            assert(x.status_code == 200) or (x.status_code == 301)
