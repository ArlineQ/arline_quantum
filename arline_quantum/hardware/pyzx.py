# Copyright (c) 2019-2022 Turation Ltd

from arline_quantum.gate_sets.pyzx import PyzxGateSet
from arline_quantum.qubit_connectivities.qubit_connectivity import All2All, Line
from arline_quantum.hardware.hardware import Hardware


class PyzxAll2All(Hardware):
    """Fully Connected Quantum Hardware Configuration with PyZX Gate Set

    **Description:**

        qubit_connectivity : :class:`.All2All`

        gate_set : :class:`.PyzxGateSet`

        num_gates : infinity

        cost_function : Cost Function ID

        noise_model : Noise Model ID

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
            gate_set=PyzxGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
        )


class PyzxLine(Hardware):
    """Nearest Neighbour Quantum Hardware Configuration with PyZX Gate Set

    **Description:**

        num_qubits : number of qubits

        qubit_connectivity : :class:`.Line`

        gate_set : :class:`.PyzxGateSet`

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
            gate_set=PyzxGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
        )
