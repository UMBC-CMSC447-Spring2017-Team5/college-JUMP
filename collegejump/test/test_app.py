#!env/bin/python3

import pytest
import requests
debug_f = "debug_out"

@pytest.fixture
def collegejump():
    import collegejump
    return collegejump


@pytest.fixture
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
        d = open(debug_f, 'a')
        x = app.get(base_url)
        d.write("test_http_index\n")
        d.write(str(x))
        d.close()
        assert(x.status_code == 301)

    '''
    Test the rest of the urls via HTTP response codes.
    Errs out when one of the response codes isn't 200 (OK)
    For debug info check file 'debug_out' off the main directory.
    '''
    def test_http_site(self, collegejump, app):
        d = open(debug_f, 'a')
        d.write("test_http_site\n")
        #add urls here as needed
        url_list = ['announcement/', 'calendar']
        base_url = 'http://localhost:8088/'
        for u in url_list:
            d.write('\t' + base_url + u + '\n')
            x = app.get(base_url + u + '\n')
            d.write('\t' + str(x) + '\n')
            if(x.status_code != 200):
                d.write("test broke on url=" + u)
            assert(x.status_code == 200)     
        d.close()
