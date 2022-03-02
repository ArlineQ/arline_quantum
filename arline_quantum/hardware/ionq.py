# Copyright (c) 2019-2022 Turation Ltd

from arline_quantum.gate_sets.ionq import IonqGateSet
from arline_quantum.qubit_connectivities.qubit_connectivity import All2All, Line
from arline_quantum.hardware.hardware import Hardware


class IonqAll2All(Hardware):
    """Fully ConnectedQuantum Hardware Configuration with IonQ Gate Set

    **Description:**

        num_qubits : number of qubits

        qubit_connectivity : fully connected

        gate_set : :class:`.IonqGateSet`

        num_gates : infinity

        cost_function : Cost Function ID

        noise_model : Noise Model ID

        qubit_cost : equal, 0
    """

    def __init__(
        self,
        num_qubits
    ):
        connectivity = All2All(num_qubits)
        super().__init__(
            self.__class__.__name__,
            qubit_connectivity=connectivity,
            gate_set=IonqGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
            single_qubit_gate_fidelity=0.9998,
            two_qubit_gate_fidelity=0.99,
        )


class IonqLine(Hardware):
    """Nearest Neighbour Quantum Hardware Configuration with IonQ Gate Set

    **Description:**

        num_qubits : number of qubits

        qubit_connectivity : :class:`.Line`

        gate_set : :class:`.IonqGateSet`

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
            gate_set=IonqGateSet().reduce_gate_set(num_qubits),
            num_gates=None,
            single_qubit_gate_fidelity=0.9998,
            two_qubit_gate_fidelity=0.99,
        )
