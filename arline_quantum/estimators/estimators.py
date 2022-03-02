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
from arline_quantum.gates.cnot import Cnot


class Estimator:
    """Abstract class for estimator"""

    registered_estimator_classes = {}

    @classmethod
    def register_estimator(cls, estimator_class):
        cls.registered_estimator_classes[estimator_class.__name__] = estimator_class

    @classmethod
    def from_config(cls, cfg):
        return cls.registered_estimator_classes[cfg["class"]](**cfg["args"])

    def calculate_cost(self, gate_chain):
        raise NotImplementedError()


class IbmCostFunction(Estimator):
    """Ibm Cost Function Class

    Basic cost function from IBM Quantum Volume paper https://arxiv.org/abs/2008.08571.
    :math:`C^{-1} = K^d \prod_i F^{1q}_i \prod_j F^{1q}_j`
    where
        :math: `C` - gate chain cost
        :math: `K` - depth penalty factor (depends on T1/T2 coherence gates times)
        :math: `F^{1q}` - single qubit gate fidelity
        :math: `F^{2q}` - two qubit gate fidelity
    Our definition of :math:`C` is equal to inverse :math:`C^{-1}` from the IBM paper.
    """

    def __init__(
        self,
        depth_penalty_factor=0.995,
    ):
        super().__init__()
        self.depth_penalty_factor = depth_penalty_factor

    def calculate_cost(self, gate_chain):
        depth_penalty_factor = self.depth_penalty_factor
        depth = gate_chain.get_depth()
        num_1q_gates = gate_chain.get_n_qubit_gate_count(n=1)
        num_2q_gates = gate_chain.get_n_qubit_gate_count(n=2)
        f1q = gate_chain.quantum_hardware.single_qubit_gate_fidelity
        f2q = gate_chain.quantum_hardware.two_qubit_gate_fidelity
        # If we detect three qubit gates, four qubit gates etc return np.nan, since cost function is undefined
        n_qubits = set([g.gate.num_qubits for g in gate_chain.chain])
        if max(n_qubits) >= 3:
            return np.nan
        # Otherwise return cost function
        cost = -np.log(depth_penalty_factor) * depth - np.log(f1q) * num_1q_gates - np.log(f2q) * num_2q_gates
        return cost


class BasicCostFunction(Estimator):
    def calculate_cost(self, gate_chain):
        return len(gate_chain)


class GateTypeCostEstimator(Estimator):
    def __init__(self, gates_costs={}, default_cost=0):
        self.gates_costs = gates_costs
        self.default_cost = default_cost

    def _gate_connection_cost(self, gate_conn):
        gate_name = gate_conn._gate.name
        try:
            return self.gates_costs[gate_name]
        except KeyError:
            return self.default_cost

    def calculate_cost(self, gate_chain):
        return sum([self._gate_connection_cost(conn) for conn in gate_chain])


class CnotEqualCostFunction(GateTypeCostEstimator):
    def __init__(
        self,
        cnot_cost=1,
    ):
        super().__init__({"Cnot": cnot_cost})


class CnotExpCostFunction(Estimator):
    def __init__(
        self,
        cnot_cost=1,
    ):
        super().__init__()
        self.cnot_cost = cnot_cost

    def calculate_cost(self, gate_chain):
        return self.cnot_cost * np.exp(gate_chain.get_num_gates_by_gate_type(Cnot))


class CnotCountExpCostFunction(Estimator):
    def __init__(
        self,
        cnot_cost=1,
    ):
        super().__init__()
        self.cnot_cost = cnot_cost

    def calculate_cost(self, gate_chain):
        cnot_count = gate_chain.get_num_gates_by_gate_type(Cnot)
        return self.cnot_cost ** cnot_count


class GateEqualCostFunction(Estimator):
    def __init__(
        self,
        cost_by_qubit_number={1: 1, 2: 100},
    ):
        super().__init__()
        self.cost_by_qubit_number = cost_by_qubit_number

    def calculate_cost(self, gate_chain):
        return sum([gate_chain.get_num_gates_by_qubits(n) * cost for n, cost in self.cost_by_qubit_number.items()])


class TwoQubitGateCountCostFunction(Estimator):
    def __init__(
        self,
    ):
        super().__init__()

    def calculate_cost(self, gate_chain):
        return gate_chain.get_n_qubit_gate_count(2)


class DepthCostEstimator(Estimator):
    def __init__(self, gates=None):
        self.gates = gates

    def depth_by_qubit(self, gate_connections, quantum_hardware):
        d = [0 for q in range(quantum_hardware.num_qubits)]
        for gate_conn in gate_connections:
            if self.gates is not None and gate_conn._gate.name not in self.gates:
                continue
            for q in gate_conn._connections:
                d[q] += 1
        return d

    def calculate_cost(self, gate_chain):
        d = self.depth_by_qubit(gate_chain, gate_chain.quantum_hardware)
        return max(d)


class BasicNoiseModel(Estimator):
    def calculate_cost(self, gate_chain):
        return 0


Estimator.register_estimator(IbmCostFunction)
Estimator.register_estimator(BasicCostFunction)
Estimator.register_estimator(CnotEqualCostFunction)
Estimator.register_estimator(CnotCountExpCostFunction)
Estimator.register_estimator(GateEqualCostFunction)
Estimator.register_estimator(BasicNoiseModel)
Estimator.register_estimator(CnotExpCostFunction)
Estimator.register_estimator(DepthCostEstimator)
Estimator.register_estimator(GateTypeCostEstimator)
Estimator.register_estimator(TwoQubitGateCountCostFunction)
