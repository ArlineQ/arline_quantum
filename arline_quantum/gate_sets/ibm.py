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


from arline_quantum.gates.u1 import U1
from arline_quantum.gates.u2 import U2
from arline_quantum.gates.u3 import U3
from arline_quantum.gates.cnot import Cnot
from arline_quantum.gates.identity import I
from arline_quantum.gate_sets.gate_set import GateSet


class IbmGateSet(GateSet):
    """IBM Gate Set

    **Description:**

        IBM Gate Set

        [:class:`.U1`, :class:`.U2`, :class:`.U3`, :class:`.Cnot`, :class:`.I`]
    """

    def __init__(self):
        super().__init__(self.__class__.__name__, [U1, U2, U3, Cnot, I])
