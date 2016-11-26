import os
import redis
from secrets import MASTER_NODE, MASTER_PORT
import networkx as nx
from networkx.readwrite import json_graph
import json


class ConnectionManager:
    def __init__(self):
        self.__node__ = None
        self.__port__ = None
        self.conn = None
        self.graph = nx.DiGraph()

    def set_connection(self, node=None, port=None):
        self.__node__ = node or MASTER_NODE
        self.__port__ = port or MASTER_PORT
        self.conn = redis.StrictRedis(host=self.__node__, port=self.__port__)

    def add_graph(self, input_graph):
        for path in input_graph:
            self.graph.add_path(path)
        print self.graph
        print json_graph.adjacency_data(self.graph)

    def save_graph(self, name, graph):
        text = json_graph.adjacency_data(graph)
        self.conn.set(name, json.dumps(text))

    def get_graph(self, name):

        result = self.conn.get(name)
        graph = json_graph.adjacency_graph(json.loads(result))
        print graph.edges()
        return None


    def delete_value(self):
        return None

    def add_value(self):
        return None