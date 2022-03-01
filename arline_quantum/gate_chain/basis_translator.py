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

from arline_quantum.gates.u1 import U1
from arline_quantum.gates.u2 import U2
from arline_quantum.gates.u3 import U3

from arline_quantum.gates.rx import Rx
from arline_quantum.gates.rz import Rz
from arline_quantum.gates.r import R
from arline_quantum.gates.h import H

from arline_quantum.gates.cnot import Cnot

from arline_quantum.gates.xx import Xx


from qiskit.quantum_info.synthesis.one_qubit_decompose import OneQubitEulerDecomposer

from qiskit.transpiler.passes.optimization.optimize_1q_gates import Optimize1qGates
from qiskit.transpiler.passes.basis.basis_translator import BasisTranslator
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.circuit.library.standard_gates.equivalence_library import StandardEquivalenceLibrary as std_eqlib
from arline_quantum.gate_chain.gate_chain import GateChain

from arline_quantum.gate_sets.google import GoogleGateSet
from arline_quantum.gate_sets.ibm import IbmGateSet
from arline_quantum.gate_sets.ionq import IonqGateSet
from arline_quantum.gate_sets.rigetti import RigettiGateSet
from arline_quantum.gate_sets.pyzx import PyzxGateSet
from arline_quantum.gate_sets.arline import ArlineGateSet
from arline_quantum.gate_sets.cx_rz_rx import CnotRzRxGateSet
from arline_quantum.gate_sets.voqc import VoqcGateSet


class ArlineTranslator:
    """Gate Chain Translator Class (backbone for gate set rebase)
    """

    def __init__(self, single_q_tol=1e-8):
        self.single_q_tol = single_q_tol

    def merge_u3_gates(self, gate_chain):
        dag = circuit_to_dag(gate_chain.convert_to("qiskit"))
        dag = Optimize1qGates(basis=['u3']).run(dag)
        new_chain = GateChain.convert_from(dag_to_circuit(dag), format_id="qiskit")
        return new_chain

    def rebase_to_u3_and_2q_gate(self, gate_chain, g_name_2q):
        circ = gate_chain.convert_to("qiskit")
        dag = BasisTranslator(std_eqlib, target_basis=['u3', g_name_2q]).run(circuit_to_dag(circ))
        dag = Optimize1qGates(basis=['u3']).run(dag)
        new_chain = GateChain.convert_from(dag_to_circuit(dag), format_id="qiskit")
        return new_chain

    def rebase_cx_to_rxx(self, gate_chain):
        tmp_chain = gate_chain
        new_chain = GateChain(tmp_chain.quantum_hardware)
        for el in tmp_chain.chain:
            g, conn, cregs = el.gate, el.connections, el.cregs
            if isinstance(g, Cnot):
                new_chain.add_gate(Rx(-np.pi / 2), [conn[0]])
                new_chain.add_gate(Rz(np.pi / 2), [conn[0]])
                new_chain.add_gate(Rx(-np.pi / 2), [conn[0]])
                new_chain.add_gate(Xx(-np.pi / 2), conn)
                new_chain.add_gate(Rz(np.pi / 2), [conn[0]])
                new_chain.add_gate(Rx(-np.pi / 2), [conn[0]])
                new_chain.add_gate(Rx(-np.pi / 2), [conn[1]])
            else:
                new_chain.add_gate(g, conn, cregs)
        return new_chain

    def rebase_to_ibm(self, gate_chain):
        new_chain = self.rebase_to_u3_and_2q_gate(gate_chain, "cx")
        new_chain.quantum_hardware.gate_set = IbmGateSet()
        return new_chain

    def rebase_to_google(self, gate_chain):
        tmp_chain = self.rebase_to_u3_and_2q_gate(gate_chain, "cz")
        new_chain = GateChain(tmp_chain.quantum_hardware)
        new_chain.quantum_hardware.gate_set = GoogleGateSet()
        for el in tmp_chain.chain:
            g, conn, cregs = el.gate, el.connections, el.cregs
            if isinstance(g, U3):
                theta, phi, lam, _ = OneQubitEulerDecomposer()._params_u3(g.u)
                if not np.isclose(phi + lam, 0, self.single_q_tol):
                    new_chain.add_gate(Rz(phi + lam), conn)
                if not (np.isclose(theta, 0, self.single_q_tol) and
                        np.isclose(phi + np.pi/2, 0, self.single_q_tol)):
                    # TODO: submit PR to Qiskit with R-gate (temporary disable R)
                    # new_chain.add_gate(R(theta, phi + np.pi/2), conn)
                    # r(theta, phi) = u3(theta, phi - pi / 2, -phi + pi / 2)
                    new_chain.add_gate(U3(theta, phi - np.pi/2, -phi + np.pi / 2), conn)
            else:
                new_chain.add_gate(g, conn, cregs)
        return new_chain

    def rebase_to_ionq(self, gate_chain):
        tmp_chain = self.rebase_to_u3_and_2q_gate(gate_chain, "cx")
        tmp_chain = self.rebase_cx_to_rxx(tmp_chain)
        # Merge U3 gates (do not touch rxx gates)
        tmp_chain = self.rebase_to_u3_and_2q_gate(tmp_chain, "rxx")
        new_chain = GateChain(tmp_chain.quantum_hardware)
        new_chain.quantum_hardware.gate_set = IonqGateSet()
        for el in tmp_chain.chain:
            g, conn, cregs = el.gate, el.connections, el.cregs
            if isinstance(g, U3):
                angles = OneQubitEulerDecomposer()._params_zxz(g.u)
                if not np.isclose(angles[2], 0, self.single_q_tol):
                    new_chain.add_gate(Rz(angles[2]), conn)
                if not np.isclose(angles[0], 0, self.single_q_tol):
                    new_chain.add_gate(Rx(angles[0]), conn)
                if not np.isclose(angles[1], 0, self.single_q_tol):
                    new_chain.add_gate(Rz(angles[1]), conn)
            else:
                new_chain.add_gate(g, conn, cregs)
        return new_chain

    def rebase_to_rigetti(self, gate_chain):
        tmp_chain = self.rebase_to_u3_and_2q_gate(gate_chain, "cz")
        new_chain = GateChain(tmp_chain.quantum_hardware)
        new_chain.quantum_hardware.gate_set = RigettiGateSet()

        Rx_plus_pi2 = Rx.make_discrete(np.pi / 2)()
        Rx_minus_pi2 = Rx.make_discrete(-np.pi / 2)()

        for el in tmp_chain.chain:
            g, conn, cregs = el.gate, el.connections, el.cregs
            if isinstance(g, U3):
                angles = OneQubitEulerDecomposer()._params_zyz(g.u)
                if not np.isclose(angles[2], 0, self.single_q_tol):
                    new_chain.add_gate(Rz(angles[2]), conn)
                if not np.isclose(angles[0], 0, self.single_q_tol):
                    new_chain.add_gate(Rx_plus_pi2, conn)
                    new_chain.add_gate(Rz(angles[0]), conn)
                    new_chain.add_gate(Rx_minus_pi2, conn)
                if not np.isclose(angles[1], 0, self.single_q_tol):
                    new_chain.add_gate(Rz(angles[1]), conn)
            else:
                new_chain.add_gate(g, conn, cregs)
        return new_chain

    def rebase_to_pyzx(self, gate_chain):
        tmp_chain = self.rebase_to_u3_and_2q_gate(gate_chain, 'cx')
        new_chain = GateChain(tmp_chain.quantum_hardware)
        for el in tmp_chain.chain:
            g, conn, cregs = el.gate, el.connections, el.cregs
            if isinstance(g, U3):
                angles = OneQubitEulerDecomposer()._params_zxz(g.u)
                if not np.isclose(angles[2], 0, self.single_q_tol):
                    new_chain.add_gate(Rz(angles[2]), conn)
                if not np.isclose(angles[0], 0, self.single_q_tol):
                    new_chain.add_gate(Rx(angles[0]), conn)
                if not np.isclose(angles[1], 0, self.single_q_tol):
                    new_chain.add_gate(Rz(angles[1]), conn)
            else:
                new_chain.add_gate(g, conn, cregs)
        new_chain.quantum_hardware.gate_set = PyzxGateSet()
        return new_chain

    def rebase_to_cx_rz_rx(self, gate_chain):
        tmp_chain = self.rebase_to_u3_and_2q_gate(gate_chain, 'cx')
        new_chain = GateChain(tmp_chain.quantum_hardware)
        for el in tmp_chain.chain:
            g, conn, cregs = el.gate, el.connections, el.cregs
            if isinstance(g, U3):
                angles = OneQubitEulerDecomposer()._params_zxz(g.u)
                if not np.isclose(angles[2], 0, self.single_q_tol):
                    new_chain.add_gate(Rz(angles[2]), conn)
                if not np.isclose(angles[0], 0, self.single_q_tol):
                    new_chain.add_gate(Rx(angles[0]), conn)
                if not np.isclose(angles[1], 0, self.single_q_tol):
                    new_chain.add_gate(Rz(angles[1]), conn)
            else:
                new_chain.add_gate(g, conn, cregs)
        new_chain.quantum_hardware.gate_set = CnotRzRxGateSet()
        return new_chain

    def rebase_to_voqc(self, gate_chain):
        new_chain = GateChain(gate_chain.quantum_hardware)
        circ = gate_chain.convert_to("qiskit")
        dag = BasisTranslator(std_eqlib, target_basis=['u1', 'u2', 'u3', 'rz', 'rx',
                              'x', 's', 'sdg', 't', 'tdg', 'h', 'cx']).run(circuit_to_dag(circ))
        dag = Optimize1qGates(basis=['u3']).run(dag)
        tmp_chain = GateChain.convert_from(dag_to_circuit(dag), format_id="qiskit")
        for el in tmp_chain.chain:
            g, conn, cregs = el.gate, el.connections, el.cregs
            if isinstance(g, U1):
                phi = g.args[0]
                new_chain.add_gate(Rz(phi), conn)
            elif isinstance(g, U2):
                theta, phi = g.args
                new_chain.add_gate(Rz(phi-np.pi/2), conn)
                new_chain.add_gate(H(), conn)
                new_chain.add_gate(Rz(np.pi/2), conn)
                new_chain.add_gate(H(), conn)
                new_chain.add_gate(Rz(theta+np.pi/2), conn)
            elif isinstance(g, U3):
                theta, phi, lmbda = g.args
                new_chain.add_gate(Rz(lmbda-np.pi/2), conn)
                new_chain.add_gate(H(), conn)
                new_chain.add_gate(Rz(theta), conn)
                new_chain.add_gate(H(), conn)
                new_chain.add_gate(Rz(phi+np.pi/2), conn)
            elif isinstance(g, Rx):
                phi = g.args[0]
                new_chain.add_gate(H(), conn)
                new_chain.add_gate(Rz(phi), conn)
                new_chain.add_gate(H(), conn)
            else:
                new_chain.add_gate(g, conn, cregs)
        new_chain.quantum_hardware.gate_set = VoqcGateSet()
        return new_chain

    def rebase_to_arline(self, gate_chain):
        new_chain = self.rebase_to_u3_and_2q_gate(gate_chain, "cx")
        new_chain.quantum_hardware.gate_set = ArlineGateSet()
        return new_chain
