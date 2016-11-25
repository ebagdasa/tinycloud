import os

MASTER_NODE=os.getenv('MASTER_NODE')

connection = None


class Environment:
    def __init__(self):
        self.node = MASTER_NODE
