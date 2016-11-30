from fabric.api import *
from json import JSONEncoder
import secrets
from tinycloud.env import ConnectionManager


class Node(JSONEncoder):

    def __init__(self, name, ip, port, user, pwd, virt_type='virtual'):
        super(Node, self).__init__()
        self.name = name
        self.ip = ip
        self.port = port
        self.user = user
        self.pwd = pwd
        self.virt_type = virt_type

    def cmd(self, cmd, use_sudo=True):
        with settings(host_string='{0}@{1}'.format(self.user, self.ip), port=self.port):
            res = sudo(cmd) if use_sudo else run(cmd)
            # print res
        return res
