import os
import tempfile
import config
import subprocess
import json
import shutil
import server_lib.utils as utils

class DeploymentException(Exception):
    pass


class Package:
    def __init__(self, file):
        """
        Initialize the package

        The full path (not relative) of the package must be given
        """
        self.filename = file
        self.name = "unknown-app"
        self.loaded = False
        self.workdir = tempfile.mkdtemp(dir=config.WORKDIR)

    def log_action(self, action):
        print("[PACKAGE] {0} action {1}".format(self.name, action))

    def load(self):
        """
        Load the package and all the metadata
        """
        self.log_action("Load package {0} in {1}".format(self.filename, self.workdir))
        try:
            self.log_action("Unzip package in {0}".format(self.workdir))
            child = subprocess.Popen(["tar", "zxf" , self.filename], cwd=self.workdir)
            child.communicate()
            if child.returncode != 0:
                raise DeploymentException("Invalid package archive - cannot extract")
        except Exception as e:
            raise DeploymentException("Invalid package archive" + str(e))

        if not os.path.isfile(self.workdir + "/manifest.json"):
            self.log_action("Did not found manifest in {0}".format(self.workdir))
            raise DeploymentException("No manifest.json")

        try:
            self.manifest = json.load(open(self.workdir + "/manifest.json"))
            self.name = self.manifest["name"]
        except Exception:
            self.log_action("Cannot load JSON in {0}".format(self.workdir))
            raise DeploymentException("Cannot load the json file")

        for file in self.manifest["files"]:
            fullpath = "{0}/{1}".format(self.workdir, file["source"])
            if not os.path.exists(fullpath):
                self.log_action("Missing file in {0}".format(self.workdir))
                raise DeploymentException("File {0} from manifest does not exist")

        self.loaded = True

    def deploy(self):
        """
        Deploy the package on the host

        It takes all necessary actions to deploy the package on the host:
           * pre-installation scripts
           * remove packages
           * install package
           * remove files
           * copy files
           * post-installation scripts

        If it fails, it returns a simple DeploymentException

        The package needs to be loaded beforehand
        """
        if not self.is_loaded():
            return;

        try:
            for cmd in self.manifest["pre-installation"]:
                utils.run_command(cmd)
        except Exception:
            raise DeploymentException("Fail to run pre-installation commands")

        try:
            self.remove_packages()
        except Exception:
            raise DeploymentException("Fail to remove packages")

        try:
            self.install_packages()
        except Exception:
            raise DeploymentException("Fail to install packages")

        try:
            self.remove_files()
        except Exception as e:
            raise DeploymentException("Fail to remove files {0}".format(str(e)))

        try:
            self.copy_files()
        except Exception as e:
            raise DeploymentException("Fail to copy files {0}".format(str(e)))

        try:
            for cmd in self.manifest["post-installation"]:
                utils.run_command(cmd)
        except Exception:
            raise DeploymentException("Fail to run post-installation commands")
        return True

    def remove_files(self):
        """
        Remove files only if they exist

        The list of files is given in the manifest file

        The package needs to be loaded beforehand
        """
        if not self.is_loaded():
            return;

        for f in self.manifest["files-remove"]:

            if os.path.isfile(f["path"]):
                os.remove(f["path"])

    def copy_files(self):
        """
        Copy files
        """
        if not self.is_loaded():
            return;
        for f in self.manifest["files"]:
            print("f=" + str(f))
            source = "{0}/{1}".format(self.workdir,f["source"])
            destination = f["target"]
            owner = f["owner"]
            group = f["group"]
            mode = f["mode"]
            self.log_action("Copying {0} to {1}".format(source, destination))
            shutil.copy(source, destination)
            os.chmod(destination, int(mode))

            # Python library requires the UID/GID. We are calling
            # the shell command so that we can use username/groupname
            utils.run_command("chown {0} {1}".format(owner, destination))
            utils.run_command("chgrp {0} {1}".format(group, destination))

    def remove_packages(self):
        """
        Remove all the packages.

        The package names are specified in the manifest file as follow:
         {
         ...
         "conflicting-packages: [ ...]
         ...
         }

        The package needs to be loaded beforehand
        """
        if not self.is_loaded():
            return;
        for package in self.manifest["conflicting-packages"]:
            self.log_action("remove package {0}".format(package))
            utils.remove_package(package)


    def install_packages(self):
        """
        Install all the necessary packages.

        The package names are specified in the manifest file as follow:
         {
         ...
         "required-packages: [ ...]
         ...
         }

        The package needs to be loaded beforehand
        """
        if not self.is_loaded():
            return;
        for package in self.manifest["required-packages"]:
            self.log_action("install package {0}".format(package))
            utils.install_package(package)

    def is_loaded(self):
        return self.loaded

