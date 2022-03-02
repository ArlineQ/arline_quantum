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


from arline_quantum.gate_sets.ibm import IbmGateSet
from arline_quantum.qubit_connectivities.ibm_connectivity import Rueschlikon, Falcon, Ourense
from arline_quantum.qubit_connectivities.ibm_connectivity import RueschlikonSymmetrical
from arline_quantum.qubit_connectivities.qubit_connectivity import All2All, Line
from arline_quantum.hardware.hardware import Hardware


class IbmAll2All(Hardware):
    """Fully Connected Quantum Hardware Configuration with IBM Gate Set

    **Description:**

        num_qubits : number of qubits

        qubit_connectivity : :class:`.All2All`

        gate_set : :class:`.IbmGateSet`

        num_gates : infinity

        qubit_cost : equal, 0
    """

    def __init__(
        self,
        num_qubits,
    ):
        connectivity = All2All(num_qubits)
        super().__init__(
            self.__class__.__name__,
            qubit_connectivity=connectivity,
            gate_set=IbmGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
        )


class IbmLine(Hardware):
    """Nearest Neighbour Quantum Hardware Configuration with IBM Gate Set

    **Description:**

        num_qubits : number of qubits

        qubit_connectivity : :class:`.Line`

        gate_set : :class:`.IbmGateSet`

        num_gates : infinity

        qubit_cost : equal, 0
    """

    def __init__(
        self,
        num_qubits,
    ):
        connectivity = Line(num_qubits)
        super().__init__(
            self.__class__.__name__,
            qubit_connectivity=connectivity,
            gate_set=IbmGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
        )


class IbmRueschlikon(Hardware):
    """IBM Rueschlikon Quantum Hardware Configuration

    **Description:**

        num_qubits : 16

        qubit_connectivity : :class:`.Rueschlikon`

        gate_set : :class:`.IbmGateSet`

        num_gates : infinity

        qubit_cost : equal, 0
    """

    def __init__(
        self,
    ):
        connectivity = Rueschlikon()
        super().__init__(
            self.__class__.__name__,
            qubit_connectivity=connectivity,
            gate_set=IbmGateSet().reduce_gate_set(connectivity.num_qubits),
            num_gates=None,
        )


class IbmRueschlikonSymmetrical(Hardware):
    """IBM Rueschlikon Symmetrical Quantum Hardware Configuration

    **Description:**

        num_qubits : 16

        qubit_connectivity : :class:`.RueschlikonSymmetrical`

        gate_set : :class:`.IbmGateSet`

        num_gates : infinity

        cost_function : Cost Function ID

        noise_model : Noise Model ID

        qubit_cost : equal, 0
    """

    def __init__(
        self,
    ):
        connectivity = RueschlikonSymmetrical()
        super().__init__(
            self.__class__.__name__,
            qubit_connectivity=connectivity,
            gate_set=IbmGateSet().reduce_gate_set(connectivity.num_qubits),
            num_gates=None,
        )


class IbmOurense(Hardware):
    """IBM Ourense Quantum Hardware Configuration

    **Description:**

        num_qubits : 5

        qubit_connectivity : :class:`.Ourense`

        gate_set : :class:`.IbmGateSet`

        num_gates : infinity

        qubit_cost : equal, 0
    """

    def __init__(
        self,
    ):
        connectivity = Ourense()
        super().__init__(
            self.__class__.__name__,
            qubit_connectivity=connectivity,
            gate_set=IbmGateSet().reduce_gate_set(connectivity.num_qubits),
            num_gates=None,
            single_qubit_gate_fidelity=0.9996,
            two_qubit_gate_fidelity=0.99
        )


class IbmFalcon(Hardware):
    """IBM Falcon Quantum Hardware Configuration

    **Description:**

        num_qubits : 27

        qubit_connectivity : :class:`.Falcon`

        gate_set : :class:`.IbmGateSet`

        num_gates : infinity

        qubit_cost : equal, 0
    """

    def __init__(
        self,
    ):
        connectivity = Falcon()
        super().__init__(
            self.__class__.__name__,
            qubit_connectivity=connectivity,
            gate_set=IbmGateSet().reduce_gate_set(connectivity.num_qubits),
            num_gates=None,
            single_qubit_gate_fidelity=0.9996,
            two_qubit_gate_fidelity=0.99
        )
