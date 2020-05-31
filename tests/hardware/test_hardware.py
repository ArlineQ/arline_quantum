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

from arline_quantum.hardware import hardware_by_name
from arline_quantum.qubit_connectivity.qubit_connectivity import All2All


class TestHardware(unittest.TestCase):
    def test_all2all_connectivity_creation(self):
        hw = hardware_by_name({"hardware": {"gate_set": ["Cnot"], "num_qubits": 2, "qubit_connectivity": "All2All"}})
        self.assertTrue(isinstance(hw.qubit_connectivity, All2All))


if __name__ == "__main__":
    unittest.main()
