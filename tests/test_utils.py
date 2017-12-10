import os
import unittest

from server_lib.utils import is_valid_user
from server_lib.utils import run_command


class TestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_login(self):
        self.assertFalse(is_valid_user("admin", "plop"))
        self.assertTrue(is_valid_user("admin", "foobar"))

    def test_run_command(self):
        self.assertFalse(run_command("/efiwoefi/wefwief"))
        self.assertTrue(run_command("/bin/ls"))

if __name__ == '__main__':
    unittest.main()
