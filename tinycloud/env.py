import os
import redis
from secrets import MASTER_NODE, MASTER_PORT
import networkx as nx
from networkx.readwrite import json_graph
import json
import matplotlib.pyplot as plt

type_shape={'service': 'o', 'sensor':'s', 'actuator': 'p'}
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
        new_flow = [[y[0:3] for y in x] for x in input_flow]
        for flow in input_flow:
            for app in flow:
                if not self.graph.has_node(app[0:3]):
                    raise Exception('Please define application {0} first.'.format(app))
                elif self.graph.node[app[0:3]]['full_name'] != app:
                    raise Exception('Names of app abbreviations {0} and '
                                    '{1} don\'t match.'.format(self.graph.node[app[0:3]]['full_name'], app))
        flow = nx.DiGraph()
        for path in new_flow:
            flow.add_path(path, weight=1)

        # copy node attributes
        for node in flow.nodes():
            flow.node[node] = self.graph.node[node]

        self.flows[name] = flow
        print "graph {0} created: {1}".format(name, json_graph.adjacency_data(flow))
        self.save_graph(name, flow)
        self.merge_graphs(flow)

    def add_node(self, name, app_type, data, impl='virtual'):
        self.graph.add_node(name[0:3], full_name=name, type=app_type, data=data, impl=impl, node_shape=type_shape[app_type], node_color=data_color[data])
        print 'Added new node: {0}'.format(name)
        self.save_graph('main', self.graph)

    def draw_graph(self, name):
        graph = self.get_graph(name)
        labels = nx.get_edge_attributes(graph, 'weight')
        plt.clf()
        pos=nx.circular_layout(graph)

        nodes = self.get_node_list(graph)

        nx.draw_networkx_nodes(graph, pos, nodelist=nodes['sensor']['name'],
                               node_color=nodes['sensor']['color'], node_shape='s', node_size=700, with_labels=True)
        nx.draw_networkx_nodes(graph,pos,nodelist=nodes['service']['name'], node_size=700, node_color=nodes['service']['color'], node_shape='o', with_labels=True)
        nx.draw_networkx_nodes(graph,pos,nodelist=nodes['actuator']['name'], node_size=700, node_color=nodes['actuator']['color'], node_shape='p', with_labels=True)

        nx.draw_networkx_edges(graph, pos)

        nx.draw_networkx_labels(graph, pos, font_size=16)

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

    def test_fill(self):
        import random

        n = 10
        types = ['service', 'sensor', 'actuator']
        data=['private', 'public']
        impls = ['physical', 'virtual']
        nodes = {'sensor': {'name':[], 'color':[]},
                 'actuator': {'name':[], 'color':[]},
                 'service':{'name':[], 'color':[]}}
        for i in range(0, n):
            type = random.choice(types)
            data_i = random.choice(data)
            if type=='sensor' or type=='actuator':
                impl = random.choice(impls)
            else:
                impl = 'physical'
            self.add_node(name=str(i).zfill(3), app_type=type, data=data_i, impl=impl)

        for i in range(0, 10):
            flow = list()
            remaining_nodes = self.graph.nodes()
            length = random.randint(2, 10)
            print "length {0}".format(length)
            for j in range(0, length):
                if j==0:
                    available_nodes = self.get_nodes_by_type(self.graph, 'type', 'sensor', remaining_nodes)
                    if not available_nodes:
                        break
                    node = random.choice(available_nodes)
                    remaining_nodes.remove(node)
                elif j == length-1:
                    available_nodes = self.get_nodes_by_type(self.graph, 'type', 'actuator', remaining_nodes)
                    available_nodes = self.get_nodes_by_type(self.graph, 'data', self.graph.node[flow[j-1]]['data'], available_nodes)
                    if not available_nodes:
                        break
                    node = random.choice(available_nodes)
                    remaining_nodes.remove(node)
                else:
                    print flow
                    print j
                    if self.graph.node[flow[j-1]]['type']=='sensor':
                        available_nodes = remaining_nodes
                    else:
                        available_nodes = self.get_nodes_by_type(self.graph, 'type', 'service', remaining_nodes)
                    if not available_nodes:
                        break
                    node = random.choice(available_nodes)
                    remaining_nodes.remove(node)
                flow.append(node)
                # if self.graph.node[node]['impl']=='physical':
                #     break
            self.add_flow(i, [flow])


    @staticmethod
    def get_nodes_by_type(graph, attr_name, app_type, nodes):
        list_nodes = list()
        for node, value in nx.get_node_attributes(graph, attr_name).iteritems():
            if value == app_type and node in nodes:
                list_nodes.append(node)
        return list_nodes




