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


import unittest
import numpy as np

from numpy import pi
from itertools import permutations

from arline_quantum.gates.u3 import U3
from .test_gate import compare_matrix_to_qiskit

qasm_symbols = [
    (2 * pi, -2 * pi, pi / 30, "u3(2*pi,-2*pi,0.10471975511965977)"),
    (-2 * pi, 2 * pi, -pi / 30, "u3(-2*pi,2*pi,-0.10471975511965977)"),
]


class TestU3(unittest.TestCase):
    def test_qasm(self):
        for a in qasm_symbols:
            with self.subTest(a=a):
                qasm_gate = U3(a[0], a[1], a[2]).to_qasm()
                qasm_ref = a[3]
                np.testing.assert_equal(qasm_gate, qasm_ref)

    def test_matrix(self):
        num_qubits = 2
        connections = list(permutations(range(num_qubits), 1))

        for theta in np.linspace(0, 2 * pi, 5):
            for phi in np.linspace(0, 2 * pi, 5):
                for lam in np.linspace(0, 2 * pi, 5):
                    for conn in connections:
                        with self.subTest(conn=conn, theta=theta, phi=phi, lam=lam):
                            compare_matrix_to_qiskit(
                                num_qubits=num_qubits, qasm_gate_name="u3", args=(theta, phi, lam), qubits=conn
                            )


if __name__ == "__main__":
    unittest.main()
