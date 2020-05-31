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


from arline_quantum.qubit_connectivity.qubit_connectivity import QubitConnectivity


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
