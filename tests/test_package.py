import unittest
from server_lib.package import Package, DeploymentException
import os


class TestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_load(self):
        cwd = os.getcwd()
        package = Package(cwd + "/tests/package.tgz")
        package.load()
        self.assertTrue(package.is_loaded())

        package2 = Package(cwd + "/tests/package-without-manifest.tgz")
        with self.assertRaises(DeploymentException) as context:
            package2.load()
            self.assertTrue('No manifest.json' in context.exception)

        package3 = Package(cwd + "/tests/package-without-file.tgz")
        with self.assertRaises(DeploymentException) as context:
            package3.load()
            self.assertTrue('File index.php from manifest does not exist' in context.exception)

    def test_deploy(self):
        cwd = os.getcwd()
        package = Package(cwd + "/tests/test-empty.tgz")
        package.load()
        self.assertTrue(package.is_loaded())

        package.manifest["files"][0]["owner"] = os.getuid()
        package.manifest["files"][0]["owner"] = os.getgid()

        self.assertTrue(package.deploy())

if __name__ == '__main__':
    unittest.main()
