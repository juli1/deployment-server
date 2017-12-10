#!venv/bin/python


import socketserver
import config
from server_lib.http import  RequestHandler

def start_server():
    print ("Starting server on port {0}".format(config.PORT))

    handler = RequestHandler
    httpd = socketserver.TCPServer(("", config.PORT), handler)
    httpd.allow_reuse_address = True
    httpd.serve_forever()


if __name__ == "__main__":
    start_server()


