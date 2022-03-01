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


from arline_quantum.gate_sets.google import GoogleGateSet
from arline_quantum.qubit_connectivities.qubit_connectivity import All2All, Line
from arline_quantum.qubit_connectivities.google_connectivity import Sycamore
from arline_quantum.hardware.hardware import Hardware


class GoogleAll2All(Hardware):
    """Fully Connected Quantum Hardware Configuration with Google Gate Set

    **Description:**

        num_qubits : number of qubits

        qubit_connectivity : :class:`.All2All`

        gate_set : :class:`.GoogleGateSet`

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
            gate_set=GoogleGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
            single_qubit_gate_fidelity=0.9995,
            two_qubit_gate_fidelity=0.991,
        )


class GoogleLine(Hardware):
    """Nearest Neighbour Quantum Hardware Configuration with Google Gate Set

    **Description:**

        qubit_connectivity : :class:`.Line`

        gate_set : :class:`.GoogleGateSet`

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
            gate_set=GoogleGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
            single_qubit_gate_fidelity=0.9995,
            two_qubit_gate_fidelity=0.991,
        )


class GoogleSycamore(Hardware):
    """Sycamore Quantum Hardware Configuration with Google Gate Set

    **Description:**

        qubit_connectivity : :class:`.Sycamore`

        gate_set : :class:`.GoogleGateSet`

        num_gates : infinity

        qubit_cost : equal, 0
    """

    def __init__(
        self,
    ):
        connectivity = Sycamore()
        super().__init__(
            self.__class__.__name__,
            qubit_connectivity=connectivity,
            gate_set=GoogleGateSet().reduce_gate_set(connectivity.num_qubits),
            num_gates=None,
            single_qubit_gate_fidelity=0.9995,
            two_qubit_gate_fidelity=0.991,
        )
