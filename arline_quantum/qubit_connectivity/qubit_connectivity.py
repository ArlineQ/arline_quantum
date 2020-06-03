# Arline Quantum
# Copyright (C) 2019-2020 Turation Ltd
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

        :param connnections: nodes numbers
        :type connnections: tuple

        :return:
            :py:const:`True`: if qubit is connected to other

            :py:const:`False`: if it is not connected

        :rtype: bool
        """
        # pairs = combinations(connections, 2)
        # for p in pairs:
        # if self.connectivity[tuple(p)] == 0:
        # return False
        # return True
        if len(connections) == 1:
            return True
        elif self.connectivity[connections[0]][connections[1]] == 0:
            return False
        else:
            return True

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

    @staticmethod
    def from_config(hardware_cfg):
        num_qubits = hardware_cfg["num_qubits"]
        if "qubit_connectivity" in hardware_cfg:
            if isinstance(hardware_cfg["qubit_connectivity"], str):
                if hardware_cfg["qubit_connectivity"] == "All2All":
                    return All2All(num_qubits)
                else:
                    raise Exception("Wrong connectivity ID")

        if "adj_matrix" in hardware_cfg:
            return QubitConnectivity(
                "adj_matrix {}".format(hardware_cfg["adj_matrix"]), num_qubits, adj_matrix=hardware_cfg["adj_matrix"],
            )

        if "connections_list" in hardware_cfg:
            return QubitConnectivity(
                "connections_list {}".format(hardware_cfg["connections_list"]),
                num_qubits,
                connections_list=hardware_cfg["connections_list"],
            )

        return All2All(num_qubits)


class All2All(QubitConnectivity):
    """Fully-Connected Qubit Connectivity

    **Description:**

        Fully-Connected Qubit Connectivity

    :param num_qubits: number of qubits
    :type num_qubits: int
    """

    def __init__(self, num_qubits):
        super().__init__("all2all", num_qubits, adj_matrix=np.ones((num_qubits, num_qubits)) - np.eye(num_qubits))



