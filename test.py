#!env/bin/python3

import collegejump
import unittest

class CollegeJUMPTestCase(unittest.TestCase):
    def setUp(self):
        self.app = collegejump.app.test_client()

    def tearDown(self):
        pass

    def test_version_present(self):
        """Ensure that the version string is present on the index page."""
        version = collegejump.__version__
        rv = self.app.get('/')
        assert bytes(version, encoding='UTF-8') in rv.data

if __name__ == '__main__':
    unittest.main()
