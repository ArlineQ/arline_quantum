# Arline Quantum
# Copyright (C) 2019-2022 Turation Ltd
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

from arline_quantum.gate_chain import gate_chain
from arline_quantum.hardware import hardware_by_name
from arline_quantum.gates.measure import Measure


class GateConnection:
    def __init__(self, quantum_hardware, gate, connections, cregs=[]):
        self._quantum_hardware = quantum_hardware
        self._gate = gate
        self._connections = connections
        self._cregs = cregs
        # if isinstance(self._gate, Gate):
        #     self._u = self._gate.u

    def __str__(self):
        return str(self.gate) + "_" + "&".join([str(c) for c in self.connections])

    @property
    def connections(self):
        return self._connections

    @property
    def cregs(self):
        return self._cregs

    @property
    def quantum_hardware(self):
        return self._quantum_hardware

    @property
    def gate(self):
        return self._gate

    def dagger(self):
        c = self.__class__(self._quantum_hardware, self._gate, self._connections)
        c._gate = c.gate.dagger()
        c._u = None
        return c

    def to_qasm(self, qreg_name, creg_name="c"):
        # TODO: Fix for the Measure instruction
        # measure q[0] -> c[0];
        if isinstance(self.gate, Measure):
            return (
                self.gate.to_qasm()
                + " "
                + qreg_name
                + f"[{self.connections[0]}]"
                + " -> "
                + creg_name
                + f"[{self.cregs[0]}];"
            )
        return (
            self.gate.to_qasm()
            + " "
            + qreg_name
            + "["
            + ("], " + qreg_name + "[").join([str(a) for a in self.connections])
            + "];"
        )

    def commute(self, other_gate_conn, tol=1e-7):
        """ Return True if gate operators commute, False otherwise
        """
        conn1 = set(self._connections)
        conn2 = set(other_gate_conn._connections)

        if len(conn1.intersection(conn2)) == 0:
            return True

        conn_mapping = {v: k for k, v in (enumerate(conn1.union(conn2)))}

        hw_cfg = {"gate_set": [], "num_qubits": len(conn_mapping)}
        hw = hardware_by_name(hw_cfg)
        gc1 = gate_chain.GateChain(hw)
        gc2 = gate_chain.GateChain(hw)

        gc1.add_gate(self._gate, [conn_mapping[n] for n in self.connections])
        gc2.add_gate(other_gate_conn._gate, [conn_mapping[n] for n in other_gate_conn.connections])

        return (abs(gc1.matrix.dot(gc2.matrix) - gc2.matrix.dot(gc1.matrix)) < tol).all()
