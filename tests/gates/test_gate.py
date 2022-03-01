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
import numpy as np

from arline_quantum.gates import gate_by_name
from arline_quantum.gates.rx import Rx
from arline_quantum.gate_chain.gate_chain import GateChain

from qiskit import QuantumCircuit
from qiskit.quantum_info.operators import Operator


def fidelity(u1, u2):
    """Fidelity (abs) between the u2 state and the u1 gate_chain"""
    fid = np.abs(np.trace(np.matmul(u2, np.matrix(u1).H))) / len(u2)
    return fid


def compare_matrix_to_qiskit(num_qubits, qasm_gate_name, args, qubits):

    if args is not None:
        args_str = "({})".format(", ".join([str(a) for a in args]))
    else:
        args_str = ""

    conn_str = ", ".join(["q[{}]".format(q) for q in qubits])

    qasm = (
        "OPENQASM 2.0;\n"
        'include "qelib1.inc";\n'
        f"qreg q[{num_qubits}];\n"
        f"{qasm_gate_name}{args_str} {conn_str};\n"
    )

    gate_chain = GateChain.from_qasm_string(qasm)
    qiskit_circ = QuantumCircuit.from_qasm_str(qasm)
    qiskit_matrix = Operator(qiskit_circ).data
    np.testing.assert_almost_equal(fidelity(qiskit_matrix, gate_chain.matrix), 1)


class TestGateCreation(unittest.TestCase):
    def test_continuous_gate(self):
        g = Rx(2 * np.pi / 30)
        self.assertEqual(g.is_discrete, False)

    def test_make_discrete(self):
        g_ref = Rx(2 * np.pi / 30)
        g = Rx.make_discrete(2 * np.pi / 30)()
        self.assertEqual(g.is_discrete, True)
        np.testing.assert_almost_equal(g_ref.u, g.u)

    def test_conjugate_on_discrete(self):
        g_ref = Rx(2 * np.pi / 30).dagger()
        g = Rx.make_discrete(2 * np.pi / 30)().dagger()
        self.assertEqual(g.is_discrete, True)
        np.testing.assert_almost_equal(g_ref.u, g.u)

    def test_conjugate_on_discrete_twice(self):
        g_ref = Rx(2 * np.pi / 30)
        g = Rx.make_discrete(2 * np.pi / 30)().dagger().dagger()
        self.assertEqual(g.is_discrete, True)
        np.testing.assert_almost_equal(g_ref.u, g.u)

    def test_continuous_gate_by_name(self):
        g = gate_by_name("Rx")
        self.assertEqual(g.is_discrete, False)

    def test_discrete_gate_by_name(self):
        angle = 2 * np.pi / 30
        g_ref = Rx(angle)
        g = gate_by_name("Rx(2*pi/30)")()
        self.assertEqual(g.is_discrete, True)
        np.testing.assert_almost_equal(g_ref.u, g.u)

    def test_format_args(self):
        g = gate_by_name("Rx(pi/3)")()
        self.assertEqual(g.angles(representation='rational'), ['pi/3'])
        self.assertEqual(g.angles(representation='decimal'), ['1.0471975511965979'])

        g = gate_by_name("Rx(-0.15*pi)")()
        self.assertEqual(g.angles(representation='rational'), ['-3*pi/20'])
        self.assertEqual(g.angles(representation='decimal'), ['-0.15*pi'])

if __name__ == "__main__":
    unittest.main()
