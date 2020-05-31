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


from arline_quantum.gate_sets.ibm import IbmGateSet
from arline_quantum.qubit_connectivity.ibm_connectivity import Rueschlikon
from arline_quantum.qubit_connectivity.ibm_connectivity import RueschlikonSymmetrical
from arline_quantum.qubit_connectivity.qubit_connectivity import All2All
from arline_quantum.hardware.basic_hardware import BasicHardware


class IbmAll2All(BasicHardware):
    """Basic Fully Connected Quantum Hardware Configuration with IBM Gate Set

    **Description:**

        qubit_connectivity : :class:`.All2All`

        gate_set : :class:`.IbmGateSet`

        num_gates : infinity

        gate_cost : equal, 1

        gate_noise : equal, 0

        qubit_cost : equal, 0
    """

    def __init__(self, num_qubits):
        connectivity = All2All(num_qubits)
        super().__init__(
            self.__class__.__name__,
            num_qubits=num_qubits,
            qubit_connectivity=connectivity,
            gate_set=IbmGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
        )


class IbmRueschlikon(BasicHardware):
    """Basic IBM Rueschlikon Quantum Hardware Configuration

    **Description:**

        qubit_connectivity : :class:`.Rueschlikon`

        gate_set : :class:`.IbmGateSet`

        num_gates : infinity

        gate_cost : equal, 1

        gate_noise : equal, 0

        qubit_cost : equal, 0
    """

    def __init__(self):
        num_qubits = 16
        connectivity = Rueschlikon()
        super().__init__(
            self.__class__.__name__,
            num_qubits=num_qubits,
            qubit_connectivity=connectivity,
            gate_set=IbmGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
        )


class IbmRueschlikonSymmetrical(BasicHardware):
    """Basic IBM Rueschlikon Symmetrical Quantum Hardware Configuration

    **Description:**

        qubit_connectivity : :class:`.RueschlikonSymmetrical`

        gate_set : :class:`.IbmGateSet`

        num_gates : infinity

        gate_cost : equal, 1

        gate_noise : equal, 0

        qubit_cost : equal, 0
    """

    def __init__(self):
        num_qubits = 16
        connectivity = RueschlikonSymmetrical()
        super().__init__(
            self.__class__.__name__,
            num_qubits=num_qubits,
            qubit_connectivity=connectivity,
            gate_set=IbmGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
        )
