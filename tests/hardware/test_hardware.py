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

from arline_quantum.hardware import hardware_by_name
from arline_quantum.qubit_connectivities.qubit_connectivity import All2All, Line
from arline_quantum.hardware.hardware import Hardware
from arline_quantum.gate_sets.gate_set import GateSet
import numpy as np


class TestHardware(unittest.TestCase):
    def test_all2all_connectivity_creation(self):
        hw = hardware_by_name(
            {
                "gate_set": ["Cnot"],
                "qubit_connectivity": {
                    "class": "All2All",
                    "args": {
                        "num_qubits": 2,
                    }
                }
            }
        )
        self.assertTrue(isinstance(hw.qubit_connectivity, All2All))

    def test_update_name(self):
        quantum_hardware = Hardware(f"FromQasm", qubit_connectivity=All2All(0), gate_set=GateSet(f"FromQasm", []))
        np.testing.assert_equal(quantum_hardware.name, "FromQasm0Q")
        quantum_hardware.qubit_connectivity.num_qubits += 1
        quantum_hardware.update_name()
        np.testing.assert_equal(quantum_hardware.name, "FromQasm1Q")

    def test_line_connectivity_creation(self):
        hw = hardware_by_name(
            {
                "gate_set": ["Cnot"],
                "qubit_connectivity": {
                    "class": "Line",
                    "args": {
                        "num_qubits": 4,
                    }
                }
            }
        )
        self.assertTrue(isinstance(hw.qubit_connectivity, Line))

    def test_line_connectivity_creation(self):
        hw = hardware_by_name(
            {
                "class": "IbmLine",
                "args": {
                    "num_qubits": 16
                }
            }
        )
        self.assertTrue(isinstance(hw.qubit_connectivity, Line))


if __name__ == "__main__":
    unittest.main()
