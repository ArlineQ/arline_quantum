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


from arline_quantum.gates.ccnot import Ccnot
from arline_quantum.gates.ch import Ch
from arline_quantum.gates.cnot import Cnot
from arline_quantum.gates.crx import Crx
from arline_quantum.gates.cry import Cry
from arline_quantum.gates.crz import Crz
from arline_quantum.gates.cswap import Cswap
from arline_quantum.gates.cu1 import Cu1
from arline_quantum.gates.cu3 import Cu3
from arline_quantum.gates.cy import Cy
from arline_quantum.gates.cz import Cz
from arline_quantum.gates.h import H
from arline_quantum.gates.identity import I
from arline_quantum.gates.r import R
from arline_quantum.gates.rx import Rx
from arline_quantum.gates.ry import Ry
from arline_quantum.gates.rz import Rz
from arline_quantum.gates.s import S, Sd
from arline_quantum.gates.swap import Swap
from arline_quantum.gates.t import T, Td
from arline_quantum.gates.u1 import U1
from arline_quantum.gates.u2 import U2
from arline_quantum.gates.u3 import U3
from arline_quantum.gates.x import X
from arline_quantum.gates.xx import Xx
from arline_quantum.gates.y import Y
from arline_quantum.gates.yy import Yy
from arline_quantum.gates.z import Z
from arline_quantum.gates.zz import Zz
from arline_quantum.gate_sets.gate_set import GateSet


class FullGateSet(GateSet):
    """Full Gate Set

    **Description:**

        Full Gate Set

        [:class:`.Ccnot`,
         :class:`.Ch`,
         :class:`.Cnot`,
         :class:`.Crx`,
         :class:`.Cry`,
         :class:`.Crz`,
         :class:`.Cswap`,
         :class:`.Cu1`,
         :class:`.Cu3`,
         :class:`.Cy`,
         :class:`.Cz`,
         :class:`.H`,
         :class:`.I`,
         :class:`.R`,
         :class:`.Rx`,
         :class:`.Ry`,
         :class:`.Rz`,
         :class:`.S`,
         :class:`.Sd`,
         :class:`.Swap`,
         :class:`.T`,
         :class:`.Td`,
         :class:`.U1`,
         :class:`.U2`,
         :class:`.U3`,
         :class:`.Cnot`,
         :class:`.I`,
         :class:`.X`,
         :class:`.Xx`,
         :class:`.Y`,
         :class:`.Yy`,
         :class:`.Z`,
         :class:`.Zz`,
        ]
    """

    def __init__(self):
        super().__init__(self.__class__.__name__,
                         [Ccnot,
                          Ch,
                          Cnot,
                          Crx,
                          Cry,
                          Crz,
                          Cswap,
                          Cu1,
                          Cu3,
                          Cy,
                          Cz,
                          H,
                          I,
                          R,
                          Rx,
                          Ry,
                          Rz,
                          S,
                          Sd,
                          Swap,
                          T,
                          Td,
                          U1,
                          U2,
                          U3,
                          Cnot,
                          I,
                          X,
                          Xx,
                          Y,
                          Yy,
                          Z,
                          Zz]
                         )
