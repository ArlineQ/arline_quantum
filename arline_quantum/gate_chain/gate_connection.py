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

import numpy as np


class GateConnection:
    def __init__(self, quantum_hardware, gate, connections):
        self._quantum_hardware = quantum_hardware
        self._gate = gate
        self._connections = connections
        self._u = self._gate.u

    def __str__(self):
        return str(self.gate) + "_" + "&".join([str(c) for c in self.connections])

    @property
    def connections(self):
        return self._connections

    @property
    def quantum_hardware(self):
        return self._quantum_hardware

    @property
    def gate(self):
        return self._gate

    def conjugate(self):
        c = self.__class__(self._quantum_hardware, self._gate, self._connections)
        c._gate = c.gate.conjugate()
        c._u = None
        return c

    def to_qasm(self, qreg_name):
        return (
            self.gate.to_qasm()
            + " "
            + qreg_name
            + "["
            + ("], " + qreg_name + "[").join([str(a) for a in self.connections])
            + "];"
        )
