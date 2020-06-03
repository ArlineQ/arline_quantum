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


from copy import deepcopy

import networkx as nx
import numpy as np

from arline_quantum.qubit_connectivity.qubit_connectivity import All2All, QubitConnectivity

from cirq import LineQubit
from qiskit.providers.models import GateConfig, QasmBackendConfiguration
from qiskit.test.mock.fake_backend import FakeBackend


class Hardware:
    """Quantum Hardware Configuration

    An abstract quantum hardware configuration class

    :param name: name of configuration
    :type name: str
    :param num_qubits: number of qubits
    :type num_qubits: int
    :param QubitConnectivity: qubit connectivity
    :param gate_set: dictionary of gates
    :type gate_set: GateSet
    :param num_gates: number of each type of gate, if :code:`num_gates[key] = -1`,
    :type num_gates: dict
        number of gates is equal to infinity
    """

    def __init__(self, name, num_qubits, gate_set, qubit_connectivity=None, num_gates=None):
        self.name = name
        self.qreg_mapping = {}

        if qubit_connectivity is not None:
            if not issubclass(type(qubit_connectivity), QubitConnectivity):
                raise Exception("qubit_connectivity must be QubitConnectivity object")

            self.qubit_connectivity = qubit_connectivity
        else:
            self.qubit_connectivity = All2All(num_qubits)

        self.num_qubits = num_qubits
        self.gate_set = gate_set

        self.num_gates = {g: -1 for g in self.gate_set.get_gate_names()}
        if num_gates is not None:
            self.num_gates.update(num_gates)

    def copy(self):
        return deepcopy(self)

    @property
    def num_qubits(self):
        return self._num_qubits

    @num_qubits.setter
    def num_qubits(self, num_qubits):
        qreg_qubits = sum([len(r) for r in self.qreg_mapping.values()])
        if num_qubits < qreg_qubits:
            raise ValueError(f"qreg contains {qreg_qubits}, can't set num_qubits = {num_qubits}")
        self._num_qubits = num_qubits
        self.qubit_connectivity.num_qubits = num_qubits

    def add_qreg_mapping(self, qreg_name, qreg_size):
        if qreg_name in self.qreg_mapping:
            raise ValueError(f"Error: Qreg name {qreg_name} already exists")
        start_qbit = sum([len(r) for r in self.qreg_mapping.values()])
        if start_qbit + qreg_size > self.num_qubits:
            raise ValueError(f"Hardware can't fit qreg {qreg_size} with size {qreg_name}")
        self.qreg_mapping[qreg_name] = {v: v + start_qbit for v in range(qreg_size)}

    def qreg_qubit_index(self, qreg_name, qreg_qubit):
        return self.qreg_mapping[qreg_name][qreg_qubit]

    def calculate_gate_chain_cost(self, gate_chain):
        raise NotImplementedError()

    def calculate_gate_chain_noise(self, *args):
        raise NotImplementedError()

    def print_config(self):
        """Print Configuration
        """
        print("Configuration: ", self.name)
        print("Number of Qubits: ", self.num_qubits)
        print("Qubit Connectivity: ", str(self.qubit_connectivity))
        print("Gate Set: ", str(self.gate_set))

    def convert_to_qiskit_hardware(self):
        configuration = QasmBackendConfiguration(
            backend_name=self.name,
            backend_version="0.0.0",
            n_qubits=self.num_qubits,
            basis_gates=["u1", "u2", "u3", "cx", "id"],  # TODO check gate sets
            simulator=False,
            local=True,
            conditional=False,
            open_pulse=False,
            memory=False,
            max_shots=65536,
            gates=[GateConfig(name="TODO", parameters=[], qasm_def="TODO")],
            coupling_map=self.qubit_connectivity.get_coupling_map(),
        )
        hardware = FakeBackend(configuration)
        return hardware

    def convert_to_nx_graph(self):
        adj_matrix = self.qubit_connectivity.connectivity
        if not np.array_equal(adj_matrix, adj_matrix.T):
            raise Exception("CirQ graph supports only non-directed adjacency graphs")
        graph = nx.Graph()
        for edge in self.qubit_connectivity.get_coupling_map():
            graph.add_edges_from([(LineQubit(edge[0]), LineQubit(edge[1]))])
        return graph

    def convert_to_cirq_hardware(self):
        return self.convert_to_nx_graph()
