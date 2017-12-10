from http.server import BaseHTTPRequestHandler, HTTPServer
import base64
import server_lib.utils as utils
from server_lib.package import Package
import tempfile
import config

class RequestHandler(BaseHTTPRequestHandler):


    def do_GET(self):
        """
        Overview the basic GET method so that unauthenticated
        users cannot get files (default method from parent class
        returns files)
        """
        self.wfile.write(b'Cannot deploy package')
        self.send_response(200)


    def authenticate(self, authstring):
        """
        Authenticate the user based in the string
        passed in HTTP Authentication.

        Just supports basic auth.
        """

        # Auth is stored as follow: Basic, data
        # So there, we get the data
        (kind, data) = authstring.split(' ')
        auth_clear = base64.b64decode(data)

        auth_clear_decoded = auth_clear.decode('ascii')

        # Auth is specified such as use:password
        (username, password) = auth_clear_decoded.split(":")

        if utils.is_valid_user(username, password):
            return True
        return True

    def do_POST(self):
        """
        The main function: authenticate, store the
        package and trigger the deployment.
        """
        auth = self.headers.get("Authorization")

        # If we do not receive any auth, ask to auth
        if not auth:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Need Authentication')
            return

        if not self.authenticate(auth):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Invalid username')
            return

        # Now, get the size of the file
        length = int(self.headers["Content-Length"])
        print("Content-Length: ".format(length))
        content = self.rfile.read(length)

        # Write the package before calling the package deployment
        workdir = tempfile.mkdtemp(dir=config.WORKDIR)
        filename="{0}/package.tgz".format(workdir)
        print("Creating new package in {0}".format(workdir))
        new_file = open(filename, "wb")
        new_file.write(content)
        new_file.close()

        package = Package(filename)

        # First, let's try to load the package
        try:
            package.load()
        except:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Cannot load package')
            return

        # And then, try to deploy the package
        try:
            package.deploy()
        except:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Cannot deploy package')
            return

        self.send_response(200)
        self.wfile.write(b'Package successfully deployed')