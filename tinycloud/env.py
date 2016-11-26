import os
import redis

MASTER_NODE=os.getenv('MASTER_NODE')
MASTER_PORT=os.getenv('MASTER_PORT')

connection = None


class ConnectionManager:
    def __init__(self):
        self.__node__ = None
        self.__port__ = None
        self.connection = None

    def set_connection(self, node=None, port=None):
        self.__node__ = node or MASTER_NODE
        self.__port__ = port or MASTER_PORT
        self.connection = redis.StrictRedis(host=self.__node__, port=self.__port__)

    def get_value(self):
        return None

    def add_graph(self):

        return None

    def delete_value(self):
        return None

    def add_value(self):
        return None