# Arline Quantum
# Copyright (C) 2019-2022 Turation Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import numpy as np
from itertools import permutations


class QubitConnectivity:
    """Qubit Connectivity

    **Description:**

        An abstract qubit connectivity class

    :param name: name of connectivity
    :type name: str
    :param num_qubits: number of qubits
    :type num_qubits: int
    :param adj_matrix: adjacency matrix, 2D array of shape (num_qubits, num_qubits)
    :type adj_matrix: list
    :param connections_list: list of tuples, each tuple describes one connection if form `(qubit_from, qubit_to)`
    :type connections_list: list
    """

    def __init__(self, name, num_qubits, connections_list=None, adj_matrix=None):
        if connections_list is None and adj_matrix is None:
            raise Exception("Please specify one of parameters: connections_list or adj_matrix")
        if connections_list is not None and adj_matrix is not None:
            raise Exception("Please specify only one of parameter: connections_list or adj_matrix")

        self._name = name
        self._num_qubits = num_qubits
        if adj_matrix is not None:
            self._connectivity = np.array(adj_matrix)
        else:
            self._connectivity = np.zeros((num_qubits, num_qubits))
            self.connections_list = connections_list

    @property
    def connections_list(self):
        return [(a, b) for a, b in permutations(range(0, self.num_qubits), 2) if self._connectivity[a, b]]

    @connections_list.setter
    def connections_list(self, connections_list):
        for a, b in connections_list:
            self.add_connection(a, b)

    @property
    def name(self):
        """Return name"""
        return self._name

    @name.setter
    def name(self, value):
        """Set name

        :param value: name
        :type value: str
        """
        self._name = value

    @property
    def num_qubits(self):
        """Return number of qubits"""
        return self._num_qubits

    @num_qubits.setter
    def num_qubits(self, value):
        """Set number of qubit

        :param value: number of qubit
        :type value: int
        """
        if self._num_qubits == value:
            return
        new_conn = np.zeros(shape=(value, value))
        if value > self._num_qubits:
            new_conn[: self._num_qubits, : self._num_qubits] = self._connectivity
        else:
            new_conn = self._connectivity[:value, :value]
        self._connectivity = new_conn
        self._num_qubits = value

    @property
    def connectivity(self):
        """Return connectivity"""
        return self._connectivity

    @connectivity.setter
    def connectivity(self, value):
        """Set connectivity

        :param value: connectivity
        :type value: matrix
        """
        self._connectivity = np.array(value)

    def print_connectivity(self):
        """Print connectivity
        """
        print("Qubit connectivity name: " + self.name)
        print(self.connectivity)

    def add_connection(self, node_1, node_2):
        """Add connection between two nodes

        :param node_1: node number
        :type node_1: int
        :param node_2: node number
        :type node_2: int
        """
        self._connectivity[node_1][node_2] = 1

    def delete_connection(self, node_1, node_2):
        """Delete connection between two nodes

        :param node_1: node number
        :type node_1: int
        :param node_2: node number
        :type node_2: int
        """
        self._connectivity[node_1][node_2] = 0

    def get_total_num_nets(self):
        """Get total number of nets

        :return: number of nets

            :py:const:`False`: if it is not fully connected

        :rtype: int or bool
        """
        num_nets = 0
        for j in range(self.num_qubits):
            for i in range(self.num_qubits):
                num_nets = num_nets + self.connectivity[i][j]
        return num_nets

    def check_fully_connected(self):
        """Check fully connection qubits or not

        :return:

            :py:const:`True`: if it is fully connected

            :py:const:`False`: if it is not fully connected

        :rtype: bool
        """
        if self.get_total_num_nets() == (self.num_qubits * self.num_qubits - self.num_qubits):
            return True
        else:
            return False

    def check_connection(self, connections):
        """Check connection between qubits

        :param connections: nodes numbers
        :type connections: tuple

        :return:
            :py:const:`True`: if qubit is connected to other

            :py:const:`False`: if it is not connected

        :rtype: bool
        """

        if len(connections) == 1:
            return True
        elif len(connections) == 2:
            return self.connectivity[connections[0]][connections[1]] == 1
        else:
            # Allow connection if number of qubits the gate acts
            # on is larger then 2 (3-qubit gate, 4-qubit gate etc)
            pairs = permutations(connections, 2)
            for p in pairs:
                if self.connectivity[tuple(p)] == 0:
                    return False
            return True

    def is_connected_to_any(self, qubit, other_qubits):
        return any([self.check_connection([qubit, q]) for q in other_qubits])

    def get_num_nodes_with_given_num_connections(self, num_connections):
        """Get number of nodes with given number of connections

        num_connections (int): number of connections

        :return: number of nodes with given number of connections
        :rtype: int
        """
        num_nodes = 0
        for i in range(self.num_qubits):
            connections = self.connectivity[i].count(1)
            if connections == num_connections:
                num_nodes = num_nodes + 1
        return num_nodes

    def get_most_connected_nodes(self):
        """Get list of the most connected nodes

        :return: list of the most connected nodes
        :rtype: list
        """
        num_nodes = 0
        for i in range(self.num_qubits):
            if self.connectivity[i].count(1) > num_nodes:
                num_nodes = self.connectivity[i].count(1)
        nodes = []
        for i in range(self.num_qubits):
            if self.connectivity[i].count(1) == num_nodes:
                nodes.append(i)
        return nodes

    def get_least_connected_nodes(self):
        """Get list of the least connected nodes

        :return: list of the least connected nodes
        :rtype: list
        """
        num_nodes = self.num_qubits - 1
        for i in range(self.num_qubits):
            if self.connectivity[i].count(1) < num_nodes:
                num_nodes = self.connectivity[i].count(1)
        nodes = []
        for i in range(self.num_qubits):
            if self.connectivity[i].count(1) == num_nodes:
                nodes.append(i)
        return nodes

    def get_unconnected_qubits(self):
        """Get list of unconnected qubits

        :return: list of unconnected qubits
        """
        return [(a, b) for a, b in permutations(range(0, self.num_qubits), 2) if self.connectivity[a, b] == 0]

    def add_node(self):
        """Add node
        """
        self._connectivity.append([])
        for i in range(self.num_qubits):
            self._connectivity[self.num_qubits].append(0)
        self._num_qubits = self.num_qubits + 1
        for i in range(self.num_qubits):
            self._connectivity[i].append(0)

    def delete_node(self, node):
        """Delete node

        :param node: node number
        :type node: int
        """
        for i in range(self.num_qubits):
            self._connectivity[i].pop(self.num_qubits - 1)
        self._connectivity.pop(node)
        self._num_qubits = self.num_qubits - 1

    def find_path(self, start, end, path=[]):
        """Find path between two nodes

        :param start: start node number
        :type start: int
        :param end: end node number
        :type end: int
        :param path: list of nodes
        :type path: list

        :return: list of nodes
        :rtype: list
        """
        path = path + [start]
        if start == end:
            return path
        if self.connectivity[start].count(1) == 0:
            return None
        for (index, value) in enumerate(self.connectivity[start]):
            if (value == 1) and (index not in path):
                new_path = self.find_path(index, end, path)
                if new_path:
                    return new_path
        return None

    def find_all_paths(self, start, end, path=[]):
        """Find all paths between two nodes

        :param start: start node number
        :type start: int
        :param end: end node number
        :type end: int
        :param path: list of nodes
        :type path: list

        :return: list of paths
        :rtype: list
        """
        path = path + [start]
        if start == end:
            return [path]
        if self.connectivity[start].count(1) == 0:
            return []
        paths = []
        for (index, value) in enumerate(self.connectivity[start]):
            if (value == 1) and (index not in path):
                new_paths = self.find_all_paths(index, end, path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    def find_shortest_path(self, start, end, path=[]):
        """Find the shortest path between two nodes

        :param start: start node number
        :type start: int
        :param end: end node number
        :type end: int
        :param path: list of nodes
        :type path: list

        :return: list of nodes
        :rtype: list
        """
        path = path + [start]
        if start == end:
            return path
        if self.connectivity[start].count(1) == 0:
            return None
        shortest = None
        for (index, value) in enumerate(self.connectivity[start]):
            if (value == 1) and (index not in path):
                new_path = self.find_shortest_path(index, end, path)
                if new_path:
                    if not shortest or len(new_path) < len(shortest):
                        shortest = new_path
        return shortest

    def get_coupling_map(self):
        """Convert adj_matrix to coupling map (list of [i,j])
        """
        coupling_map = []
        for i in range(self.num_qubits):
            for j in range(self.num_qubits):
                if self.connectivity[i][j] == 1:
                    coupling_map.append([i, j])
        return coupling_map

    available_connectivity_classes = {}

    @classmethod
    def from_config(cls, hardware_cfg):
        if "qubit_connectivity" in hardware_cfg:
            if "class" in hardware_cfg["qubit_connectivity"]:
                try:
                    if hardware_cfg["qubit_connectivity"]["class"] == "All2All":
                        num_qubits = hardware_cfg["qubit_connectivity"]["args"]["num_qubits"]
                        return cls.available_connectivity_classes[hardware_cfg["qubit_connectivity"]["class"]](
                            num_qubits
                        )
                    elif hardware_cfg["qubit_connectivity"]["class"] == "Line":
                        num_qubits = hardware_cfg["qubit_connectivity"]["args"]["num_qubits"]
                        return cls.available_connectivity_classes[hardware_cfg["qubit_connectivity"]["class"]](
                            num_qubits
                        )
                    else:
                        return cls.available_connectivity_classes[hardware_cfg["qubit_connectivity"]["class"]]()
                except KeyError:
                    raise Exception("Wrong connectivity ID")

            if "adj_matrix" in hardware_cfg["qubit_connectivity"]:
                num_qubits = hardware_cfg["qubit_connectivity"]["args"]["num_qubits"]
                return QubitConnectivity(
                    "adj_matrix {}".format(hardware_cfg["qubit_connectivity"]["adj_matrix"]),
                    num_qubits,
                    adj_matrix=hardware_cfg["qubit_connectivity"]["adj_matrix"],
                )

            if "connections_list" in hardware_cfg["qubit_connectivity"]:
                num_qubits = hardware_cfg["qubit_connectivity"]["args"]["num_qubits"]
                return QubitConnectivity(
                    "connections_list {}".format(hardware_cfg["qubit_connectivity"]["connections_list"]),
                    num_qubits,
                    connections_list=hardware_cfg["qubit_connectivity"]["connections_list"],
                )
        else:
            num_qubits = hardware_cfg["num_qubits"]
            return All2All(num_qubits)

    @classmethod
    def register_connectivity_class(cls, connectivity, name=None):
        if name is None:
            name = connectivity.__name__
        cls.available_connectivity_classes[name] = connectivity


class All2All(QubitConnectivity):
    """Fully-Connected Qubit Connectivity

    **Description:**

        Fully-Connected Qubit Connectivity

    :param num_qubits: number of qubits
    :type num_qubits: int
    """

    def __init__(self, num_qubits):
        super().__init__("all2all", num_qubits, adj_matrix=np.ones((num_qubits, num_qubits)) - np.eye(num_qubits))


class Line(QubitConnectivity):
    """Nearest Neighbour Qubit Connectivity

    **Description:**

        Nearest Neighbour Qubit Connectivity

    :param num_qubits: number of qubits
    :type num_qubits: int
    """

    def __init__(self, num_qubits):
        connections_list = []
        for i in range(1, num_qubits):
            connections_list.append([i - 1, i])
            connections_list.append([i, i - 1])
        super().__init__("line", num_qubits, connections_list=connections_list)


from arline_quantum.qubit_connectivities import ibm_connectivity
from arline_quantum.qubit_connectivities import rigetti_connectivity
from arline_quantum.qubit_connectivities import google_connectivity

QubitConnectivity.register_connectivity_class(All2All)
QubitConnectivity.register_connectivity_class(Line)
QubitConnectivity.register_connectivity_class(ibm_connectivity.Rueschlikon)
QubitConnectivity.register_connectivity_class(ibm_connectivity.RueschlikonSymmetrical)
QubitConnectivity.register_connectivity_class(ibm_connectivity.Ourense)
QubitConnectivity.register_connectivity_class(rigetti_connectivity.Agave)
QubitConnectivity.register_connectivity_class(rigetti_connectivity.AgaveSymmetrical)
QubitConnectivity.register_connectivity_class(rigetti_connectivity.Aspen)
QubitConnectivity.register_connectivity_class(rigetti_connectivity.AspenSymmetrical)
QubitConnectivity.register_connectivity_class(google_connectivity.Sycamore)
