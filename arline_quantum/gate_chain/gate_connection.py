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
        self._u = None

    def __str__(self):
        return str(self.gate) + "_" + "&".join([str(c) for c in self.connections])

    @property
    def connections(self):
        return self._connections

    @property
    def u(self):
        if self._u is None:
            self._u = self._calculate_matrix()
        return self._u

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

    def _calculate_matrix(self):
        if self.gate.num_qubits == 1:
            return self._construct_1qubit()
        elif self.gate.num_qubits == 2:
            return self._construct_2qubit()
        else:
            raise NotImplementedError()

    def _construct_2qubit(self):
        """ Construct 2 qubit gatematrix
        """
        u = self.gate.u
        num_qubits = self.quantum_hardware.num_qubits

        p0 = np.array([[1, 0], [0, 0]], dtype=np.complex_)
        p1 = np.array([[0, 0], [0, 1]], dtype=np.complex_)
        l0 = np.array([[0, 1], [0, 0]], dtype=np.complex_)
        l1 = np.array([[0, 0], [1, 0]], dtype=np.complex_)

        r = self._project(num_qubits, self.connections[0], self.connections[1], u[0:2, 0:2], p0)
        r += self._project(num_qubits, self.connections[0], self.connections[1], u[2:4, 2:4], p1)
        r += self._project(num_qubits, self.connections[0], self.connections[1], u[0:2, 2:4], l0)
        r += self._project(num_qubits, self.connections[0], self.connections[1], u[2:4, 0:2], l1)

        return r

    def _project(self, num_qubits, conn1, conn2, u, p):
        op_prev = None
        for i in range(num_qubits):
            if i == conn1:
                op = p
            elif i == conn2:
                op = u
            else:
                op = np.eye(2)
            if i != 0:
                op = np.kron(op, op_prev)
            else:
                pass
            op_prev = op.copy()
        return op_prev

    def _construct_1qubit(self):
        u = self.gate.u
        num_qubits = self.quantum_hardware.num_qubits

        op_prev = None
        for i in range(num_qubits):
            if i == self.connections[0]:
                op = u
            else:
                op = np.eye(2)

            if i != 0:
                op = np.kron(op, op_prev)
            else:
                pass
            op_prev = op.copy()
            # Inserting the gate
        return op

    def to_qasm(self, qreg_name):
        return (
            self.gate.to_qasm()
            + " "
            + qreg_name
            + "["
            + ("], " + qreg_name + "[").join([str(a) for a in self.connections])
            + "];"
        )
