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
from arline_quantum.gates import Cnot, Rx, Rz, Ccnot
from arline_quantum.gate_chain.gate_chain import GateChain
from arline_quantum.hardware import hardware_by_name


class TestGateConnection(unittest.TestCase):
    def test_commute_rx(self):
        hw_cfg = {
            "gate_set": ["Cnot", "Rx", "Rz"],
            "qubit_connectivity": {
                "class": "All2All",
                "args": {
                    "num_qubits": 3,
                }
            }
        }
        hw = hardware_by_name(hw_cfg)
        gate_chain = GateChain(hw)
        gate_chain.add_gate(Rx(0.5), [0])
        gate_chain.add_gate(Rx(0.5), [0])
        self.assertTrue(gate_chain[0].commute(gate_chain[1]))

    def test_not_commute_rx_rz(self):
        hw_cfg = {
            "gate_set": ["Cnot", "Rx", "Rz"],
            "qubit_connectivity": {
                "class": "All2All",
                "args": {
                    "num_qubits": 3,
                }
            }
        }
        hw = hardware_by_name(hw_cfg)
        gate_chain = GateChain(hw)
        gate_chain.add_gate(Rx(0.5), [0])
        gate_chain.add_gate(Rz(0.5), [0])
        self.assertFalse(gate_chain[0].commute(gate_chain[1]))

    def test_commute_cnot_rz_control(self):
        hw_cfg = {
            "gate_set": ["Cnot", "Rx", "Rz"],
            "qubit_connectivity": {
                "class": "All2All",
                "args": {
                    "num_qubits": 3,
                }
            }
        }
        hw = hardware_by_name(hw_cfg)
        gate_chain = GateChain(hw)
        gate_chain.add_gate(Cnot(), [0, 1])
        gate_chain.add_gate(Rz(0.5), [0])
        self.assertTrue(gate_chain[0].commute(gate_chain[1]))

    def test_not_commute_cnot_rx_control(self):
        hw_cfg = {
            "gate_set": ["Cnot", "Rx", "Rz"],
            "qubit_connectivity": {
                "class": "All2All",
                "args": {
                    "num_qubits": 3,
                }
            }
        }
        hw = hardware_by_name(hw_cfg)
        gate_chain = GateChain(hw)
        gate_chain.add_gate(Cnot(), [0, 1])
        gate_chain.add_gate(Rx(0.5), [0])
        self.assertFalse(gate_chain[0].commute(gate_chain[1]))
