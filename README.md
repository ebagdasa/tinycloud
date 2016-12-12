TinyCloud: Cloudlet design on ARM platform.

This project aims to provide control over ARM-platform and deploy different applications on Xen and Docker instances. 
The project is designed for CS 6410 class.

To install execute: **python setup.py install**

Note: for MacOS installation of scipy module requires to add file: ~/.matplotlib/matplotlibrc with content backend: TkAgg


There are multiple functions currently available:
* Add node with virtualization type xen or containers
* Add an application
* Deploy

The project requires a file secrets.py with defined variables MASTER_NODE, MASTER_PORT.

After installation use:

`from tinycloud.server import Server`

`from tinycloud.env import ConnectionManager`

`conn = ConnectionManager()`

`conn.test_fill(10)`

`conn.draw_graph('main')`