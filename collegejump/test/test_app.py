#!env/bin/python3

import pytest

@pytest.fixture
def collegejump():
    import collegejump
    return collegejump

@pytest.fixture
def app():
    import collegejump
    return collegejump.app.test_client()

class TestCollegeJUMP():
    def test_version_present(self, collegejump, app):
        """Ensure that the version string is present on the index page."""
        version = collegejump.__version__
        rv = app.get('/')
        assert bytes(version, encoding='UTF-8') in rv.data
