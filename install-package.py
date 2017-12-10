#!venv/bin/python

import sys
import os
from server_lib.package import Package


if len(sys.argv) != 2:
    print("Please specify a package to deploy")
    sys.exit(1)

filename = sys.argv[1]

if not os.path.isfile(filename):
    print ("Package {0} is not found".format(filename))
    sys.exit(1)

package = Package(filename)

try:
    package.load()
except Exception as e:
    print("Package {0} is not valid: {1}".format(filename, str(e)))
    sys.exit(1)

try:
    package.deploy()
except Exception as e:
    print("Package {0} cannot be deployed: {1}".format(filename, str(e)))
    sys.exit(1)


print("Package {0} successfully deployed".format(filename))
sys.exit(0)