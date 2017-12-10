from passlib.hash import pbkdf2_sha256
import config
import subprocess


def is_valid_user(username, password):
    """
    Simple authentication mechanism that gets data from the passwd file

    Return True is authentication is possible, false otherwise
    """

    with open(config.PASSWORD_FILE) as f:
        for line in f:
            (u, p) = line.rstrip().split(" ")
            if u == username:
                return pbkdf2_sha256.verify(password, p)
    return False


def install_package(name):
    return run_command("apt-get install -y {0}".format(name))


def remove_package(name):
    return run_command("apt-get remove -y {0}".format(name))


def run_command(cmd):
    print("run command: {0}".format(cmd))
    try:
        child = subprocess.Popen(cmd, shell=True)
        child.communicate()
        print("{0} return code {1}".format(cmd, str(child.returncode)))
        if child.returncode != 0:
            return False
    except Exception as e:
        print("Got exception: " + str(e))
        return False
    return True
