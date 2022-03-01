# Copyright (c) 2019-2020 Turation Ltd

from arline_quantum.gates.rx import Rx
from arline_quantum.gates.rz import Rz
from arline_quantum.gates.xx import Xx

from arline_quantum.gate_sets.gate_set import GateSet


class IonqGateSet(GateSet):
    """IonQ Gate Set

    **Description:**

        Continuous Gate Set.

        [:class:`.Rx`,
         :class:`.Rz`,
         :class:`.Xx`]
    """

    def __init__(self):
        super().__init__(self.__class__.__name__, [Rx, Rz, Xx])
