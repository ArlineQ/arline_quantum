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
from itertools import permutations

import numpy as np
from numpy import pi

from arline_quantum.gates.r import R

qasm_symbols = [(2 * pi, -2 * pi, "r(2*pi,-2*pi)"), (-2 * pi, 2 * pi, "r(-2*pi,2*pi)")]


class TestR(unittest.TestCase):
    def test_qasm(self):
        for a in qasm_symbols:
            with self.subTest(a=a):
                qasm_gate = R(a[0], a[1]).to_qasm()
                print(qasm_gate)
                qasm_ref = a[2]
                np.testing.assert_equal(qasm_gate, qasm_ref)

    def test_matrix(self):
        pass # There are no r gate in current qiskit version


if __name__ == "__main__":
    unittest.main()
