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


from arline_quantum.qubit_connectivities.qubit_connectivity import QubitConnectivity


class Rueschlikon(QubitConnectivity):
    """Rueschlikon Qubit Connectivity

    **Description:**

        Rueschlikon Qubit Connectivity

    """

    def __init__(self):
        num_qubits = 16
        connections_list = [
            [1, 0],
            [1, 2],
            [2, 3],
            [3, 4],
            [3, 14],
            [5, 4],
            [6, 5],
            [6, 7],
            [6, 11],
            [7, 10],
            [8, 7],
            [9, 8],
            [9, 10],
            [11, 10],
            [12, 5],
            [12, 11],
            [12, 13],
            [13, 4],
            [13, 14],
            [15, 0],
            [15, 2],
            [15, 14],
        ]
        super().__init__("rueschlikon", num_qubits, connections_list=connections_list)


class RueschlikonSymmetrical(QubitConnectivity):
    """Rueschlikon Symmetrical Qubit Connectivity

    **Description:**

        Rueschlikon Symmetrical Qubit Connectivity

    """

    def __init__(self):
        num_qubits = 16
        connections_list = [
            [1, 0],
            [0, 1],
            [1, 2],
            [2, 1],
            [2, 3],
            [3, 2],
            [3, 4],
            [4, 3],
            [3, 14],
            [14, 3],
            [5, 4],
            [4, 5],
            [6, 5],
            [5, 6],
            [6, 7],
            [7, 6],
            [6, 11],
            [11, 6],
            [7, 10],
            [10, 7],
            [8, 7],
            [7, 8],
            [9, 8],
            [8, 9],
            [9, 10],
            [10, 9],
            [11, 10],
            [10, 11],
            [12, 5],
            [5, 12],
            [12, 11],
            [11, 12],
            [12, 13],
            [13, 12],
            [13, 4],
            [4, 13],
            [13, 14],
            [14, 13],
            [15, 0],
            [0, 15],
            [15, 2],
            [2, 15],
            [15, 14],
            [14, 15],
        ]
        super().__init__("rueschlikon_symmetrical", num_qubits, connections_list=connections_list)


class Ourense(QubitConnectivity):
    """Ourense Qubit Connectivity

    **Description:**

        Ourense Qubit Connectivity

        0 <--> 1 <--> 2
               ^
               |
               v
               3
               ^
               |
               v
               4

    """

    def __init__(self):
        num_qubits = 5
        connections_list = [[0, 1], [1, 0], [1, 2], [2, 1], [1, 3], [3, 1], [3, 4], [4, 3]]
        super().__init__("ourense", num_qubits, connections_list=connections_list)


class Falcon(QubitConnectivity):
    """Falcon Qubit Connectivity

    **Description:**

        Falcon Qubit Connectivity

    """

    def __init__(self):
        num_qubits = 27
        connections_list = [
            [0, 1],
            [1, 0],
            [1, 2],
            [1, 4],
            [2, 1],
            [2, 3],
            [3, 2],
            [3, 5],
            [4, 1],
            [4, 7],
            [5, 3],
            [5, 8],
            [6, 7],
            [7, 4],
            [7, 6],
            [7, 10],
            [8, 5],
            [8, 9],
            [8, 11],
            [9, 8],
            [10, 7],
            [10, 12],
            [11, 8],
            [11, 14],
            [12, 10],
            [12, 13],
            [12, 15],
            [13, 12],
            [13, 14],
            [14, 11],
            [14, 13],
            [14, 16],
            [15, 12],
            [15, 18],
            [16, 14],
            [16, 19],
            [17, 18],
            [18, 15],
            [18, 17],
            [18, 21],
            [19, 16],
            [19, 20],
            [19, 22],
            [20, 19],
            [21, 18],
            [21, 23],
            [22, 19],
            [22, 25],
            [23, 21],
            [23, 24],
            [24, 23],
            [24, 25],
            [25, 22],
            [25, 24],
            [25, 26],
            [26, 25],
        ]
        super().__init__("falcon", num_qubits, connections_list=connections_list)
