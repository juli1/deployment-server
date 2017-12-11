[![Build status](https://travis-ci.org/juli1/deployment-server.svg?master)](https://travis-ci.org/juli1)
[![Coverage Status](https://coveralls.io/repos/github/juli1/deployment-server/badge.svg?branch=master)](https://coveralls.io/github/juli1/deployment-server?branch=master)

# Deployment Server
This is a small deployment server application.
It is used to simply deploy packages either locally or remotely.

Packages are specified in a tarball image.
At the root of the package, a json file ```manifest.json``` specifies the package metadata:
- Files to install
- Files to remove
- Commands to execute before installing the package
- Commands to execute after installing the package


# Design

The design is very basic:
* The server is an HTTP server. Possible to use HTTPS of course
* Authentication is done using basic HTTP authentication.
* User login/password are stored in a file (```passwd``). Passwords are encrypted.
* Client issue a HTTP POST request to install a package

Things that are ***not*** managed:
* ***Multi-distribution****: this works for Ubuntu/Debian.
* ***Creation of directory***: this is by design. The installer can then check for basedir creation.


Order of operation to deploy a package is the following:
* Run pre-installation scripts
* Remove files
* Remove packages
* Install packages
* Install files
* Run post-installation scripts

## Potential enhancements
* Use the full HTTP semantics. For example, use /install-package address to install the package
* If installing a lot of package, use a thread pool to fo the installation
* Have a log reporting mechanism
** Have /install-package to install a package and return an deployment-id
** Have /get-logs?id=<deployment-id> to get the full logs

### Package metadata

The package metadata are specified in a file called ```manifest.json```.

Notes:
* The file ***must*** be in the root directory of the package archive.
* If the file does not exist, the package fail to install.
* If any file specified in the ```files``` section does not exist, the package
fails to install too.
* If any key/field is missing in the ```manifest.json``` file, installation fail.


```json
{
   "name" : "testapp",
   "pre-installation":
      [],
   "required-packages" : ["libapache2-mod-php5", "php5", "apache2"],
   "conflicting-packages" : [],
   "files" :
               [
                  {"source"  : "index.php",
                   "target"  : "/var/www/html/index.php",
                   "owner"   : "admin",
                   "group"   : "www",
                   "mode"    : "644"
                  }
               ],
   "files-remove":
               [
                  {
                   "path"  : "/var/www/html/index.html"
                  }
               ],
   "post-installation":
      [
         "/etc/init.d/apache2 restart"
      ]
}
```

There are the different meaning of each section:
* ***name***: name of the package
* ***pre-installation***: list of debian packages to install
* ***required-packages***: list of debian packages to remove
* ***files***: name of files to install with their owner/group
* ***files-remove***: list of files to remove
* ***pre-installation***: list of command to execute pre-installation
* ***post-installation***: list of commands to execute post-installation




# Installation notes
For now, this is really minimal packaging.
You can just run a virtualenv environment with all the necessary dependencies.
 
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
./server.py
```

If you want to use this on an Ubuntu/Debian system, please use
```bash
./bootstrap.sh
```

## How to use new users
Users are specified in the ```passwd``` file.
Each line specify the username and password.
The password is not stored in cleartext.
Instead, we are storing encrypted password.

To add a new user:
```bash
./add-user.py <username> <password>
```

***WARNING***: at that time, the tool just
adds stupidly the username/password. It does not check
if the name already exist or not.


### How to delete existing users
Just edit the passwd file and remove the file
with the corresponding user.


# How to Use

## Install a package locally
If you are on the host, just type the following command as root:

```bash
./install-package.py <archive>
```

For example, 

```bash
./install-package.py tests/dummy.tgz
```

## Install a package remotely

If you want to install a package remotely, use the following command:

```bash
curl -X POST --data-binary @<PACKAGE-NAME> http://<USERNAME>:<PASSWORD>@localhost:9000 
```

For example:

```bash
curl -X POST --data-binary @mypackage.tgz http://admin:foobar@localhost:9000 
```



### But the port of the server is not accessible!
If your server does not have the port open, you can just use a SSH
port forwarding:
```bash
ssh user@<server-ip>  -L <local-port>:localhost:<server-port>
```

And then just use

```bash
curl -X POST --data-binary @mypackage.tgz http://admin:foobar@localhost:<local-port>
```


# How to specify a package
Put all the files you want to package in a single directory.
Specify the ```manifest.json``` file as shown above.
Then, compress all files as follow:
```bash
tar cvvfz package.tgz *
```

The file ```package.tgz``` is your archive.




# How to run test
To run the tests:
```bash
python  -m unittest discover tests
```

And to get code coverage:
```
coverage run  --source server_lib  -m unittest discover tests
```
