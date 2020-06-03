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


from copy import copy

from arline_quantum.gates import gate_by_name, qasm_gate_table


class GateSet:
    """Gate Set

    Class to represent quantum *Gate Set*

    :param gate_list: dictionary of gates
    :type gate_list: Gate
    :param name: name of gate set
    :type name: str
    """

    def __init__(self, name, gate_list):
        self.gate_list = gate_list
        self.name = name

    @property
    def gates_by_name(self):
        return {g.__name__: g for g in self.gate_list}

    @property
    def gates_by_qasm_name(self):
        return {name: g for name, g in qasm_gate_table.items() if g in self.gate_list}

    def gate_by_name(self, gate_name):
        """
        :return: gate class by name
        :rtype: dict
        """
        return self.gates_by_name[gate_name]

    def get_gate_names(self):
        """
        :return: the list of gate names
        :rtype: list
        """
        return list(self.gates_by_name.keys())

    def is_discrete_gate_set(self):
        """Check if all gates are discrete

        :rtype: bool
        """
        for g in self.gate_list:
            if not g.is_discrete:
                return False
        return True

    def check_max_num_qubits(self):
        """Check max number of qubits for Gate Set

        :rtype: int
        """
        return max([g.num_qubits for g in self.gate_list])

    def reduce_gate_set(self, num_qubits):
        """Generate new gate set with only gates with number of cubits less than
        ``num_qubits``

        :param num_qubits: border value for qubit number
        :type num_qubits: int
        """
        if self.check_max_num_qubits() <= num_qubits:
            return self
        else:
            new_gate_set = copy(self)
            new_gate_set.name = self.name + "_strip_{}".format(num_qubits)
            new_gate_set.gate_list = [g for g in self.gate_list if g.num_qubits <= num_qubits]
            return new_gate_set

    def get_gate_set_size(self):
        """Get gate set size


        :return: size of Gate Set
        :rtype: int
        """
        return len(self.gate_list)

    def add_gate(self, gate):
        """Add gate into gate set

        :return:
        """
        if gate not in self.gate_list:
            self.gate_list.append(gate)

    def __str__(self):
        s = "{" + ", ".join(self.get_gate_names()) + "}"
        return "Gate Set {}: {}".format(self.name, s)

    def get_gate_list_str(self):
        s = "[" + ", ".join([a for a in self.get_gate_names()]) + "]"
        return s

    @staticmethod
    def from_gate_names(gate_names):
        gate_classes = [gate_by_name(name) for name in gate_names]
        name = "+".join(gate_names)
        return GateSet(name, gate_classes)

    def to_qiskit_name(self):
        gates = []
        for g in self.gate_list:
            gates.append(g.to_qiskit_name())
        return gates
