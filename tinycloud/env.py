import os
import redis
from secrets import MASTER_NODE, MASTER_PORT
import networkx as nx
from networkx.readwrite import json_graph
import json
import matplotlib.pyplot as plt

type_shape={'service': 's', 'sensor':'o', 'actuator': 'p'}
data_color={'private': 'b', 'public':'g'}


class ConnectionManager:
    def __init__(self):
        self.__node__ = None
        self.__port__ = None
        self.conn = None
        self.graph = nx.DiGraph()
        self.flows = dict()
        self.set_connection()

    def set_connection(self, node=None, port=None):
        self.__node__ = node or MASTER_NODE
        self.__port__ = port or MASTER_PORT
        self.conn = redis.StrictRedis(host=self.__node__, port=self.__port__)

    def get_conn_status(self):
        return self.conn.ping()

    def add_graph(self, input_graph):
        for path in input_graph:
            self.graph.add_path(path)
        print self.graph
        print json_graph.adjacency_data(self.graph)

    def save_graph(self, name, graph):
        text = json_graph.adjacency_data(graph)
        return self.conn.set(name, json.dumps(text))

    def get_graph(self, name):

        result = self.conn.get(name)
        graph = json_graph.adjacency_graph(json.loads(result))
        print graph.edges()
        return graph

    def merge_graphs(self, graph):
        for node in graph.nodes():
            if not self.graph.has_node(node):
                self.graph.add_node(node)
        for edge in graph.edges():
            weight = graph.get_edge_data(*edge)['weight']
            if not self.graph.has_edge(*edge):
                self.graph.add_edge(*edge, weight=weight)
            else:
                self.graph.add_edge(*edge, weight=self.graph.get_edge_data(*edge)['weight']+weight)
        self.save_graph('main', self.graph)

    def add_flow(self, name, input_flow):
        flow = nx.DiGraph()
        for path in input_flow:
            flow.add_path(path, weight=1)
        self.flows[name] = flow
        print "graph {0} created: {1}".format(name, json_graph.adjacency_data(flow))
        self.save_graph(name, flow)
        self.merge_graphs(flow)

    def add_node(self, name, type, data):
        self.graph.add_node(name, type=type, data=data, node_shape=type_shape[type], node_color=data_color[data])
        self.save_graph('main', self.graph)

    def draw_graph(self, name):
        graph = self.get_graph(name)
        labels = nx.get_edge_attributes(graph, 'weight')
        plt.clf()
        pos=nx.spectral_layout(graph)

        nodes = self.get_node_list(graph)


        nx.draw_networkx_nodes(graph,pos,nodelist=nodes['sensor']['name'],node_color=nodes['sensor']['color'],node_shape='s', with_labels=True)
        nx.draw_networkx_nodes(graph,pos,nodelist=nodes['service']['name'],node_color=nodes['service']['color'],node_shape='o', with_labels=True)
        nx.draw_networkx_nodes(graph,pos,nodelist=nodes['actuator']['name'],node_color=nodes['actuator']['color'],node_shape='p', with_labels=True)

        nx.draw_networkx_edges(graph,pos)

        nx.draw_networkx_labels(graph,pos,font_size=16)

        nx.draw_networkx_edge_labels(graph, pos=pos, edge_labels=labels)

    @staticmethod
    def get_node_list(graph):
        types = nx.get_node_attributes(graph, 'type')
        data = nx.get_node_attributes(graph, 'data')
        nodes = {'sensor': {'name':[], 'color':[]},
                 'actuator': {'name':[], 'color':[]},
                 'service':{'name':[], 'color':[]}}
        for name, type in types.iteritems():
            nodes[type]['name'].append(name)
            nodes[type]['color'].append(data_color[data[name]])
        return nodes

    def clear_graph(self, name):
        self.conn.delete(name)
