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


from copy import deepcopy

import networkx as nx
import re

from arline_quantum.qubit_connectivities.qubit_connectivity import All2All, QubitConnectivity

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
    :param qubit_connectivity: qubit connectivity
    :type qubit_connectivity: QubitConnectivity
    :param gate_set: dictionary of gates
    :type gate_set: GateSet
    :param num_gates: number of each type of gate, if :code:`num_gates[key] = -1`,
    :type num_gates: dictionary
    """

    def __init__(
        self,
        name,
        gate_set,
        qubit_connectivity,
        num_gates=None,
        single_qubit_gate_fidelity=.999,
        two_qubit_gate_fidelity=.99,
    ):
        if not isinstance(qubit_connectivity, QubitConnectivity):
            raise Exception("qubit_connectivity must be QubitConnectivity object")

        self.qubit_connectivity = qubit_connectivity
        self.name = f"{name}{self.num_qubits}Q"
        self.num_cbits = self.num_qubits
        self.gate_set = gate_set

        self.single_qubit_gate_fidelity = single_qubit_gate_fidelity
        self.two_qubit_gate_fidelity = two_qubit_gate_fidelity

        self.num_gates = {g: -1 for g in self.gate_set.get_gate_names()}
        if num_gates is not None:
            self.num_gates.update(num_gates)

    def copy(self):
        return deepcopy(self)

    @property
    def num_qubits(self):
        return self.qubit_connectivity.num_qubits

    @num_qubits.setter
    def num_qubits(self, num_qubits):
        self.qubit_connectivity.num_qubits = num_qubits

    def print_config(self):
        """Print Configuration
        """
        print("Configuration: ", self.name)
        print("Number of Qubits: ", self.num_qubits)
        print("Qubit Connectivity: ", str(self.qubit_connectivity))
        print("Gate Set: ", str(self.gate_set))

    def update_name(self):
        """Update Hardware Name
        """
        match = re.match(r"([a-z]+)([0-9]+)([a-z]+)", self.name, re.I)
        self.name = f"{match.group(1)}{self.num_qubits}Q"

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
        # if not np.array_equal(adj_matrix, adj_matrix.T):
        #     raise Exception("CirQ graph supports only non-directed adjacency graphs")
        graph = nx.Graph()
        for edge in self.qubit_connectivity.get_coupling_map():
            graph.add_edges_from([(LineQubit(edge[0]), LineQubit(edge[1]))])
        return graph

    def convert_to_cirq_hardware(self):
        return self.convert_to_nx_graph()
