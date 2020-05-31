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


from arline_quantum.gate_sets.rigetti import RigettiGateSet
from arline_quantum.qubit_connectivity.rigetti_connectivity import Agave, AgaveSymmetrical
from arline_quantum.qubit_connectivity.rigetti_connectivity import Aspen, AspenSymmetrical
from arline_quantum.qubit_connectivity.qubit_connectivity import All2All
from arline_quantum.hardware.basic_hardware import BasicHardware


class RigettiAll2All(BasicHardware):
    """Basic Fully Connected Quantum Hardware Configuration with Rigetti Gate Set

    **Description:**

        qubit_connectivity : :class:`.All2All`

        gate_set : :class:`.RigettiGateSet`

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
            gate_set=RigettiGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
        )


class RigettiAgave(BasicHardware):
    """Basic Rigetti Agave Quantum Hardware Configuration with Rigetti Gate Set and 8 Qubits

    **Description:**

        num_qubits : 8

        qubit_connectivity : :class:`.Agave`

        gate_set : :class:`.RigettiGateSet`

        num_gates : infinity

        gate_cost : equal, 1

        gate_noise : equal, 0

        qubit_cost : equal, 0
    """

    def __init__(self):
        num_qubits = 8
        connectivity = Agave()
        super().__init__(
            self.__class__.__name__,
            num_qubits=num_qubits,
            qubit_connectivity=connectivity,
            gate_set=RigettiGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
        )


class RigettiAgaveSymmetrical(BasicHardware):
    """Basic Rigetti Agave Quantum Hardware Configuration with Rigetti Gate Set and 8 Qubits
       and Symmetrical Connectivity

    **Description:**

        num_qubits : 8

        qubit_connectivity : :class:`.AgaveSymmetrical`

        gate_set : :class:`.RigettiGateSet`

        num_gates : infinity

        gate_cost : equal, 1

        gate_noise : equal, 0

        qubit_cost : equal, 0
    """

    def __init__(self):
        num_qubits = 8
        connectivity = AgaveSymmetrical()
        super().__init__(
            self.__class__.__name__,
            num_qubits=num_qubits,
            qubit_connectivity=connectivity,
            gate_set=RigettiGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
        )


class RigettiAspen(BasicHardware):
    """Basic Rigetti Aspen Quantum Hardware Configuration with Rigetti Gate Set and 16 Qubits

    **Description:**

        num_qubits : 16

        qubit_connectivity : :class:`.Aspen`

        gate_set : :class:`.RigettiGateSet`

        num_gates : infinity

        gate_cost : equal, 1

        gate_noise : equal, 0

        qubit_cost : equal, 0
    """

    def __init__(self):
        num_qubits = 16
        connectivity = Aspen()
        super().__init__(
            self.__class__.__name__,
            num_qubits=num_qubits,
            qubit_connectivity=connectivity,
            gate_set=RigettiGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
        )


class RigettiAspenSymmetrical(BasicHardware):
    """Basic Rigetti Aspen Quantum Hardware Configuration with Rigetti Gate Set and 16 Qubits

    **Description:**

        num_qubits : 16

        qubit_connectivity : :class:`.AspenSymmetrical`

        gate_set : :class:`.RigettiGateSet`

        num_gates : infinity

        gate_cost : equal, 1

        gate_noise : equal, 0

        qubit_cost : equal, 0
    """

    def __init__(self):
        num_qubits = 16
        connectivity = AspenSymmetrical()
        super().__init__(
            self.__class__.__name__,
            num_qubits=num_qubits,
            qubit_connectivity=connectivity,
            gate_set=RigettiGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
        )
