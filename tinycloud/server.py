from fabric.api import *
from json import JSONEncoder
import secrets
from tinycloud.env import ConnectionManager


class Server(JSONEncoder):

    def __init__(self, name, ip, port, user, pwd, capacity, virt_type='virtual'):
        super(Server, self).__init__()
        self.name = name
        self.ip = ip
        self.port = port
        self.user = user
        self.pwd = pwd
        self.virt_type = virt_type
        self.apps = list()
        self.capacity = capacity

    def cmd(self, cmd, use_sudo=True):
        with settings(host_string='{0}@{1}'.format(self.user, self.ip), port=self.port):
            res = sudo(cmd) if use_sudo else run(cmd)
            # print res
        return res

    def add_app(self, name, capacity=1):
        print "Capacity: " + str(capacity) + " Remaining: " + str(self.capacity)
        self.apps.append(name)
        self.capacity -= capacity
