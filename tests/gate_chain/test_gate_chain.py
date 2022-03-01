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


import unittest
from os import path
import numpy as np

from arline_quantum.gates import gate_by_name
from arline_quantum.gate_chain.gate_chain import GateChain, NoQubitConnectionError
from arline_quantum.hardware import hardware_by_name
from arline_quantum.utils.fidelity import unitary_fidelity

from qiskit import QuantumCircuit
from qiskit.quantum_info.operators import Operator


class TestGateChain(unittest.TestCase):
    def test_add_2qubit_gate(self):
        # qubits 0 and 1 is connected
        hw = hardware_by_name(
            {
                "gate_set": ["Cnot"],
                "qubit_connectivity": {
                    "adj_matrix": [[0, 1], [1, 0]],
                    "args": {
                        "num_qubits": 2,
                    }
                }
            }
        )
        gate_chain = GateChain(hw)
        angle = 2 * np.pi / 30
        cnot = gate_by_name("Cnot")()
        rx30 = gate_by_name(f"Rx({angle})")()
        rz30 = gate_by_name(f"Rz({angle})")()

        gate_chain.add_gate(cnot, [0, 1])
        gate_chain.matrix
        gate_chain.add_gate(rx30, [0])
        gate_chain.matrix
        gate_chain.add_gate(rz30, [0])
        gate_chain.matrix
        gate_chain.add_gate(rx30, [0])
        gate_chain.matrix
        gate_chain.add_gate(rz30, [1])
        gate_chain.matrix
        gate_chain.add_gate(rx30, [1])
        gate_chain.matrix
        gate_chain.add_gate(rz30, [1])

        qiskit_circ = QuantumCircuit(2)
        qiskit_circ.cx(0, 1)

        qiskit_circ.rx(2 * np.pi / 30, 0)
        qiskit_circ.rz(2 * np.pi / 30, 0)
        qiskit_circ.rx(2 * np.pi / 30, 0)
        qiskit_circ.rz(2 * np.pi / 30, 1)
        qiskit_circ.rx(2 * np.pi / 30, 1)
        qiskit_circ.rz(2 * np.pi / 30, 1)

        qiskit_matrix = Operator(qiskit_circ).data

        np.testing.assert_almost_equal(unitary_fidelity(gate_chain.matrix, qiskit_matrix), 1)

        gate_chain.add_gate(cnot, [1, 0])
        gate_chain.add_gate(rx30, [0])
        gate_chain.add_gate(rz30, [1])

        qiskit_circ.cx(1, 0)
        qiskit_circ.rx(angle, 0)
        qiskit_circ.rz(angle, 1)

        qiskit_matrix = Operator(qiskit_circ).data
        np.testing.assert_almost_equal(unitary_fidelity(gate_chain.matrix, qiskit_matrix), 1)

    def test_reverse_matrix_building_order(self):
        hw = hardware_by_name(
            {
                "gate_set": ["Cnot"],
                "qubit_connectivity": {
                    "adj_matrix": [[0, 1], [1, 0]],
                    "args": {
                        "num_qubits": 2
                    }
                }
            }
        )
        gate_chain = GateChain(hw)
        cnot = gate_by_name("Cnot")()
        rx30 = gate_by_name("Rx(30)")()
        rz30 = gate_by_name("Rz(30)")()

        gate_chain.add_gate_left(cnot, [0, 1])
        gate_chain.matrix
        gate_chain.add_gate_left(rx30, [0])
        gate_chain.matrix
        gate_chain.add_gate_left(rz30, [0])
        gate_chain.matrix
        gate_chain.add_gate_left(rx30, [0])
        gate_chain.matrix
        gate_chain.add_gate_left(rz30, [1])
        gate_chain.matrix
        gate_chain.add_gate_left(rx30, [1])
        gate_chain.matrix
        gate_chain.add_gate_left(rz30, [1])

        np.testing.assert_almost_equal(gate_chain.matrix, gate_chain._calculate_matrix())

        gate_chain.add_gate_left(cnot, [0, 1])
        gate_chain.add_gate_left(rx30, [0])
        gate_chain.add_gate_left(rz30, [0])
        gate_chain.add_gate_left(rx30, [0])
        gate_chain.add_gate_left(rz30, [1])
        gate_chain.add_gate_left(rx30, [1])
        gate_chain.add_gate_left(rz30, [1])

        np.testing.assert_almost_equal(gate_chain.matrix, gate_chain._calculate_matrix())

    def test_add_2qubit_gate_unconnected(self):
        # qubits 0 and 1 is not connected
        hw = hardware_by_name(
            {
                "gate_set": ["Cnot"],
                "qubit_connectivity": {
                    "adj_matrix": [[0, 0], [0, 0]],
                    "args": {
                        "num_qubits": 2,
                    }
                }
            }
        )
        gate_chain = GateChain(hw)
        cnot = gate_by_name("Cnot")()
        with self.assertRaises(NoQubitConnectionError):
            gate_chain.add_gate(cnot, [0, 1])  # Apply CNOT gate to unconnected qubits 0 and 1, must be an error
        with self.assertRaises(NoQubitConnectionError):
            gate_chain.add_gate(cnot, [1, 0])  # Apply CNOT gate to unconnected qubits 1 and 0, must be an error

    def test_add_2qubit_gate_unconnected_force(self):
        # qubits 0 and 1 is not connected
        hw = hardware_by_name(
            {
                "gate_set": ["Cnot"],
                "qubit_connectivity": {
                    "adj_matrix": [[0, 0], [0, 0]],
                    "args": {
                        "num_qubits": 2,
                    }
                }
            }
        )
        gate_chain = GateChain(hw)
        cnot = gate_by_name("Cnot")()
        gate_chain.add_gate(cnot, [0, 1], force_connection=True)  # Apply CNOT gate to qubits 0 and 1
        gate_chain.add_gate(cnot, [1, 0], force_connection=True)  # Apply CNOT gate to qubits 1 and 0

    def test_matrix_calculation_2q(self):
        basepath = path.dirname(__file__)
        #f = path.abspath(path.join(basepath, "matrix_test_2q.qasm"))
        f = path.abspath(path.join(basepath, "..", "qasm_files", "general", "small_angle.qasm"))
        gate_chain = GateChain.from_qasm(f)
        qiskit_circ = QuantumCircuit.from_qasm_file(f)
        qiskit_matrix = Operator(qiskit_circ).data
        np.testing.assert_almost_equal(unitary_fidelity(gate_chain.matrix, qiskit_matrix), 1)

    def test_matrix_calculation_5q(self):
        basepath = path.dirname(__file__)
        #f = path.abspath(path.join(basepath, "matrix_test_5q.qasm"))
        f = path.abspath(path.join(basepath, "..", "qasm_files", "general", "5q.qasm"))
        gate_chain = GateChain.from_qasm(f)
        qiskit_circ = QuantumCircuit.from_qasm_file(f)
        qiskit_matrix = Operator(qiskit_circ).data
        np.testing.assert_almost_equal(unitary_fidelity(gate_chain.matrix, qiskit_matrix), 1)

    def test_1000_qubit_gate_chain_creation(self):
        # qubits 0 and 1 is not connected
        hw = hardware_by_name(
            {
                "gate_set": ["Cnot"],
                "qubit_connectivity": {
                    "adj_matrix": np.ones((1000, 1000)).tolist(),
                    "args": {
                        "num_qubits": 1000,
                    }
                }
            }
        )
        gate_chain = GateChain(hw)
        cnot = gate_by_name("Cnot")()
        gate_chain.add_gate(cnot, [0, 1])  # Apply CNOT gate to qubits 0 and 1
        gate_chain.add_gate(cnot, [1, 0])  # Apply CNOT gate to qubits 1 and 0


if __name__ == "__main__":
    unittest.main()
