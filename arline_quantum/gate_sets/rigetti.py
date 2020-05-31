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


from arline_quantum.gates.cz import Cz
from arline_quantum.gates.rx import Rx
from arline_quantum.gates.rz import Rz
from arline_quantum.gate_sets.gate_set import GateSet


class RigettiGateSet(GateSet):
    """Rigetti Gate Set

    **Description:**

        Continuous Gate Set

        [:class:`.Cz`, :class:`.Rx`, :class:`.Rz`]
    """

    def __init__(self):
        super().__init__(self.__class__.__name__, [Cz, Rx, Rz])
