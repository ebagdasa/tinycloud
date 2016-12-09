import os
import redis
from secrets import MASTER_NODE, MASTER_PORT
import networkx as nx
from networkx.readwrite import json_graph
import json
import matplotlib.pyplot as plt
import knapsack
import math


type_shape={'service': 'o', 'sensor': 's', 'actuator': 'p'}
data_color={'private': 'b', 'public': 'g'}


class ConnectionManager:
    def __init__(self):
        self.__node__ = None
        self.__port__ = None
        self.conn = None
        self.graph = nx.Graph()
        self.flows = dict()
        self.servers = list()

        self.set_connection()
        self.get_servers()
        self.graph = self.get_graph('main')
        self.get_flows()

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
        print result
        if result is None:
            graph = nx.Graph()
        else:
            graph = json_graph.adjacency_graph(json.loads(result))
        print graph.edges()
        if name == 'main':
            self.graph = graph
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
        new_flow = [[y[0:2] for y in x] for x in input_flow]
        for flow in input_flow:
            for app in flow:
                if not self.graph.has_node(app[0:2]):
                    raise Exception('Please define application {0} first.'.format(app))
                elif self.graph.node[app[0:2]]['full_name'] != app:
                    raise Exception('Names of app abbreviations {0} and '
                                    '{1} don\'t match.'.format(self.graph.node[app[0:2]]['full_name'], app))
        flow = nx.DiGraph()
        for path in new_flow:
            flow.add_path(path, weight=1)

        # copy node attributes
        for node in flow.nodes():
            flow.node[node] = self.graph.node[node]

        self.flows[name] = flow
        print "graph {0} created: {1}".format(name, json_graph.adjacency_data(flow))
        self.save_flows()
        self.save_graph(name, flow)
        self.merge_graphs(flow)

    def add_new_app(self, name, app_type, data, size=1, impl='virtual'):
        self.graph.add_node(name[0:2], full_name=name, type=app_type, data=data, impl=impl, size=size,
                            node_shape=type_shape[app_type], node_color=data_color[data])
        print 'Added new node: {0}'.format(name)
        self.save_graph('main', self.graph)

    def add_new_server(self, node):

        self.servers.append(node)
        self.save_servers()

    def save_servers(self):
        
        self.conn.set('servers', json.dumps([server.__dict__ for server in self.servers]))

    def save_flows(self):
        res = dict()
        for name, flow in self.flows.iteritems():
            res[name] = json_graph.adjacency_data(flow)
        self.conn.set('flows', json.dumps(res))


    def get_flows(self):
        res = self.conn.get('flows')
        if res is None:
            return
        res = json.loads(res)
        for name, flow in res.iteritems():
            self.flows[name] = json_graph.adjacency_graph(flow, directed=True)

    def clear(self):
        self.graph = nx.Graph()
        self.flows = dict()
        self.save_flows()
        self.save_graph('main', self.graph)
        for x in self.servers:
            x.apps = list()
    
    def get_servers(self):
        from tinycloud.server import Server

        res = self.conn.get('servers')
        if res is None:
            return
        servers_json = json.loads(res)
        for server in servers_json:
            new_server = Server(name=server['name'], ip=server['ip'], port=server['port'],
                              user=server['user'], pwd=server['pwd'], capacity=server['capacity'], virt_type=server['virt_type'])
            new_server.apps = server['apps']
            self.servers.append(new_server)

    def draw_graph(self, name=None, graph=None):
        if name:
            graph = self.get_graph(name)
        labels = nx.get_edge_attributes(graph, 'weight')
        plt.clf()
        pos = {}
        # area = 6 #len(self.nodes)
        # pos_set = [[] for i in range(area)]
        # clusters = self.eigens(area)
        # # clusters = [0]*len(self.graph.nodes())
        # for i in range(0, len(self.graph.nodes())):
        #     pos_set[clusters[i]].append(self.graph.nodes()[i])
        area = len(self.servers)
        for i in range(0, area):
            angle = (i*1.0 / area) * (math.pi * 2.0)
            print angle
            cos = 20*math.cos(angle)
            sin = 20*math.sin(angle)
            pos.update(nx.circular_layout(self.servers[i].apps, scale=5, center=[cos, sin]))


        # pos.update(nx.circular_layout(pos_set[0], scale=5, center=[-20, -20]))
        # pos.update(nx.circular_layout(pos_set[1], scale=5, center=[-20,  20]))
        # pos.update(nx.circular_layout(pos_set[2], scale=5, center=[ 20,  20]))
        # pos.update(nx.circular_layout(pos_set[3], scale=5, center=[ 20, -20]))
        # pos.update(nx.circular_layout(pos_set[4], scale=5, center=[ 0,  20]))
        # pos.update(nx.circular_layout(pos_set[5], scale=5, center=[ 0, 0]))
        # pos.update(nx.circular_layout(pos_set[6], scale=5, center=[ -20, 0]))
        # pos.update(nx.circular_layout(pos_set[7], scale=5, center=[ 20, 0]))
        # pos.update(nx.circular_layout(pos_set[8], scale=5, center=[ 0, -20]))



        nodes = self.get_node_list(graph)

        nx.draw_networkx_nodes(graph, pos, nodelist=nodes['sensor']['name'],
                               node_color=nodes['sensor']['color'], node_shape='s', node_size=500, with_labels=True)
        nx.draw_networkx_nodes(graph, pos, nodelist=nodes['service']['name'], node_size=500,
                               node_color=nodes['service']['color'], node_shape='o', with_labels=True)
        nx.draw_networkx_nodes(graph, pos, nodelist=nodes['actuator']['name'], node_size=500,
                               node_color=nodes['actuator']['color'], node_shape='p', with_labels=True)

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
            if nx.degree(graph, name) >= 0:
                nodes[type]['name'].append(name)
                nodes[type]['color'].append(data_color[data[name]])
        return nodes

    def clear_graph(self, name):
        self.conn.delete(name)

    def test_fill(self, n):
        import random
        from tinycloud.server import Server

        edges = n
        # self.servers = list()
        # for x in range(1,6):
        #     server = Server(random.random(), random.random(),
        #                        random.random(),random.random(),
        #                        random.random(), 4)
        #     self.servers.append(server)
        # self.save_servers()

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
            self.add_new_app(name=str(i).zfill(2), app_type=type, data=data_i, impl=impl)

        for i in range(0, edges):
            flow = list()
            remaining_nodes = self.graph.nodes()
            length = random.randint(2, 5)
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
                        services = self.get_nodes_by_type(self.graph, 'type', 'service', remaining_nodes)
                        public = self.get_nodes_by_type(self.graph, 'data', 'private', remaining_nodes)
                        if self.graph.node[flow[j-1]]['data']=='private':
                            for pub in public:
                                if pub in services:
                                    services.remove(pub)
                        available_nodes = services + self.get_nodes_by_type(self.graph, 'type', 'sensor',
                                                                            remaining_nodes)

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
        # for node in self.graph.nodes():
        #     if nx.degree(self.graph, node) == 0:
        #         self.graph.remove_node(node)
        #         print 'removed unconnected node' + node
        self.save_graph('main', self.graph)

    @staticmethod
    def get_nodes_by_type(graph, attr_name, app_type, nodes):
        list_nodes = list()
        for node, value in nx.get_node_attributes(graph, attr_name).iteritems():
            if value == app_type and node in nodes:
                list_nodes.append(node)
        return list_nodes

    def plan_apps(self):
        area = len(self.servers)
        clusters = self.eigens(area)
        self.save_servers()

    def eigens(self, k):

        import scipy.sparse.linalg as linalg
        import scipy.cluster.vq as vq
        import scipy
        print self.graph.nodes()
        matrix = nx.normalized_laplacian_matrix(self.graph)
        eig_res = linalg.eigsh(matrix, len(self.graph.nodes())-1)[1]

        eig_res = scipy.delete(eig_res, scipy.s_[k+1:], 1)
        eig_res = scipy.delete(eig_res, 0, 1)

        norm = scipy.sqrt(eig_res*eig_res).sum(axis=1)
        eig_res = eig_res/norm.reshape(len(self.graph.nodes()),1)

        result = vq.kmeans2(eig_res, k, iter=100)[1]
        print result
        result = self.knap(k, result)
        print result
        print self.graph.nodes()
        for place in range(0, len(result)):
            app = self.graph.nodes()[place]
            self.servers[result[place]].add_app(app, self.graph.node[app]['size'])

        return result

    def knap(self, servers, spectr):
        result = [-1]*len(spectr)
        length = len(spectr)

        spectr = [x+1 for x in spectr]
        # size = [nx.degree(self.graph, node) for node in self.graph.nodes()]
        size = [self.graph.node[x]['size'] for x in self.graph.nodes()]
        capacity = [x.capacity for x in self.servers]
        print "capacity: " + str(capacity)
        weight = spectr
        print "size"
        print size

        for i in range(0, len(self.servers)):
            print "weight"
            print weight
            res = knapsack.knapsack(size, weight).solve(capacity[i])
            print res
            res = res[1]

            for j in res:
                # print "node {0} for id {1}".format(self.graph.nodes()[j], j)
                result[j] = i
                weight[j] = 0
        print "result"
        print result
        return result

    def get_remaining_apps(self):
        existing_nodes = list()
        for server in self.servers:
            existing_nodes.extend(server.apps)
        new_apps = [x for x in self.graph.nodes() if x not in existing_nodes]
        return new_apps
