#!venv/bin/python

import sys
from passlib.hash import pbkdf2_sha256

username = sys.argv[1]
clear = sys.argv[2]

print ("Adding user {0} with password {1}".format(username, clear))

password = pbkdf2_sha256.hash(clear)

with open("passwd", "a") as f:
    f.write("{0} {1}".format(username, password))

print ("User {0} added".format(username))
