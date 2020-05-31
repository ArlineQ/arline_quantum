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


from arline_quantum.hardware.hardware import Hardware


class BasicHardware(Hardware):
    """Basic Quantum Hardware Configuration with gate noise is equal to 0 for each gate and gate cost is equal to 1

    **Description:**

        gate_cost : equal, 1

        gate_noise : equal, 0
    """

    def __init__(self, name, num_qubits, gate_set, qubit_connectivity=None, num_gates=None):
        super().__init__(
            name=name,
            num_qubits=num_qubits,
            qubit_connectivity=qubit_connectivity,
            gate_set=gate_set,
            num_gates=num_gates,
        )

    def calculate_gate_chain_cost(self, gate_chain):
        return len(gate_chain)

    def calculate_gate_chain_noise(self, gate_chain):
        return 0
