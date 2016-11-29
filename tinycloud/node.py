from fabric.api import *
import secrets


class Node:

    def __init__(self, ip, port, user, pwd):
        self.ip = ip
        self.port = port
        self.user = user
        self.pwd = pwd

    def cmd(self, cmd, use_sudo=True):
        with settings(host_string='{0}@{1}'.format(self.user, self.ip), port=self.port):
            res = run(cmd)
            print res
            return res
