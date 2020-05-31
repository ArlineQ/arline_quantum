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


from arline_quantum.gates.cnot import Cnot
from arline_quantum.gates.h import H
from arline_quantum.gates.s import Sd, S
from arline_quantum.gates.t import Td, T
from arline_quantum.gate_sets.gate_set import GateSet


class CliffordTGateSet(GateSet):
    """Clifford + T Gate Set

    .. Note::
        This is Universal Gate Set

    **Description:**

        Discrete Gate Set

        [:class:`.H`, :class:`.S`, :class:`.Sd`, :class:`.Cnot`, :class:`.T`, :class:`.Td`]
    """

    def __init__(self):
        super().__init__(self.__class__.__name__, [H, S, Sd, T, Td, Cnot])
