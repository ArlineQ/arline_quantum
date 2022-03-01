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


from collections import OrderedDict, deque
from copy import copy
from itertools import islice
from string import ascii_lowercase, ascii_uppercase
import pickle

import numpy as np
from sympy.combinatorics.permutations import Permutation

from arline_quantum.gate_chain.gate_connection import GateConnection
from arline_quantum.gate_sets.gate_set import GateSet
from arline_quantum.gates import qasm_gate_table as qasm_gate_table_all
from arline_quantum.gates.cnot import Cnot
from arline_quantum.gates.gate import Gate
from arline_quantum.gates.instruction import Instruction
from arline_quantum.gates.u3 import U3
from arline_quantum.gates.swap import Swap
from arline_quantum.gates.measure import Measure
from arline_quantum.gates.barrier import Barrier
from arline_quantum.hardware.hardware import Hardware
from arline_quantum.qasm_parser.qasmparser import QasmParser
from arline_quantum.qubit_connectivities.qubit_connectivity import All2All, QubitConnectivity
from arline_quantum.gates.gate import Gate
from qiskit.exceptions import QiskitError


class NoQubitConnectionError(Exception):
    """Exception raised when placing gate to qubits that is not connected
    """

    def __init__(self, connections, gate):
        self.connection = connections
        self.gate = gate

    def __str__(self):
        return "Error: Qubits {} aren't connected for {}".format(", ".join(map(str, self.connection)), self.gate)


class GateChain:
    """Gate Chain Class

    :param quantum_hardware: Quantum hardware configuration

    :ivar list chain: gate chain, list of :class:`GateConnection`
    :ivar list chain_labels: printed labels
    :ivar np.array matrix: unitary matrix
    """

    def __init__(self, quantum_hardware):
        self.chain = deque()
        self.quantum_hardware = quantum_hardware
        self._matrix = None  # Cashed gate chain unitary

        self._new_gates_cnt_right = 0  # Used to perform incremental matrix update
        self._new_gates_cnt_left = 0  # Used to perform incremental matrix update

        self.chain_labels = []

        self.qreg_mapping = {}
        self.creg_mapping = {}

        # Initialise default qreg_mapping
        if self.quantum_hardware.num_qubits > 0:
            self.qreg_mapping["q"] = {q: q for q in range(self.quantum_hardware.num_qubits)}
            self.creg_mapping["c"] = {c: c for c in range(self.quantum_hardware.num_cbits)}

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.chain[key]
        if isinstance(key, slice):
            return list(islice(self.chain, key.start, key.stop, key.step))

    @property
    def matrix(self):
        """Calculate unitary matrix corresponding to the gate chain.
        Supports lazy matrix calculation, the call of self.matrix
        will result in recalculation of cashed unitary U = self._matrix.
        In order to update the cashed unitary after new gates were added to the
        gate chain we first evaluate the unitary of the appended gates U_new_gates.
        Then the resulting cashed unitary is the product U_new_gates * U or U * U_new_gates
        depending on whatever the new gates were appended
        to the beginning or end of the gate chain.
        """
        num_qubits = self.quantum_hardware.num_qubits
        if len(self.qreg_mapping) == 0: # If there is no qreg in gate chain
            self._matrix = np.eye(2 ** num_qubits, dtype=np.complex_)
            return self._matrix
        if self.quantum_hardware is None:
            raise Exception("Quantum hardware isn't defined")
        if self._matrix is not None and 2 ** num_qubits != self._matrix.shape[0]:
            print("Warning: Number of qubits changed in hardware")
            self._matrix = None

        if self._matrix is None:
            self._matrix = self._calculate_matrix()
            self._new_gates_cnt_right = 0
            self._new_gates_cnt_left = 0
        if self._new_gates_cnt_left > 0:
            # This part of code supposed to implement tensor contraction
            # of U_new_gates corresponding to the gates added to the end
            # of the chain and cashed unitary self._matrix.
            left_m = np.eye(2 ** num_qubits, dtype=np.complex_)
            for gate_connection in islice(self.chain, 0, self._new_gates_cnt_left):
                left_m = self._add_unitary(gate_connection.gate, gate_connection.connections, left_m)
            self._matrix = np.matmul(self._matrix, left_m)
            self._new_gates_cnt_left = 0
        if self._new_gates_cnt_right > 0:
            for gate_connection in islice(self.chain, len(self.chain) - self._new_gates_cnt_right, len(self.chain)):
                self._matrix = self._add_unitary(gate_connection.gate, gate_connection.connections, self._matrix)
            self._new_gates_cnt_right = 0

        # Add virtual swap gates corresponding to the relabeling of input/output qubits
        matrix_after_relabeling = self._add_virtual_swaps(self._matrix)
        return matrix_after_relabeling

    def add_gate(self, gate, connections, cregs=[], force_connection=False):
        """Place gate to circuit

        :param gate: gate object
        :type gate: Instruction
        :param connections: qubits to place the gate
        :type connections: tuple
        :param force_connection: don't check qubit connection
        :type force_connection: bool

        :raises NoQubitConnectionError: when there is no connection between qubits
        """
        if self.quantum_hardware is None:
            raise Exception("Quantum hardware isn't defined")
        # TODO: Check why issubclass returns False
        # if not (issubclass(type(gate), Instruction)):
        #     raise Exception("Gate isn't Instruction type")
        if not force_connection and not self.quantum_hardware.qubit_connectivity.check_connection(connections):
            raise NoQubitConnectionError(connections, gate)
        gate_connection = GateConnection(self.quantum_hardware, gate, connections, cregs)
        self.chain.append(gate_connection)
        self._new_gates_cnt_right += 1

    def add_gate_left(self, gate, connections, cregs=[], force_connection=False):
        """Place gate to left end of the circuit

        :param gate: gate object
        :type gate: Instruction
        :param connections: qubits to place the gate
        :type connections: tuple
        :param force_connection: don't check qubit connection
        :type force_connection: bool

        :raises NoQubitConnectionError: when there is no connection between qubits
        """
        if self.quantum_hardware is None:
            raise Exception("Quantum hardware is not set")
        if not (issubclass(type(gate), Instruction)):
            raise Exception("Gate isn't Instruction type")
        if not force_connection and not self.quantum_hardware.qubit_connectivity.check_connection(connections):
            raise NoQubitConnectionError(connections, gate)
        gate_connection = GateConnection(self.quantum_hardware, gate, connections, cregs)
        self.chain.appendleft(gate_connection)
        # self.noise = self.calculate_noise()
        self._new_gates_cnt_left += 1

    def insert_gate(self, gate, connections, position, cregs=[], force_connection=False):
        """Place gate at a given position

        :param gate: gate object
        :type gate: Instruction
        :param connections: qubits to place the gate
        :type connections: tuple
        :param position: index of the element before which to insert, in case of 0 gate will be places at
        :type position: int
            the front of the circuit, and len(circuit) is equivalent to add_gate()
        :param force_connection: don't check qubit connection
        :type force_connection: bool

        :raises NoQubitConnectionError: when there is no connection between qubits
        """
        if position == 0:
            return self.add_gate_left(gate, connections, force_connection)

        if self.quantum_hardware is None:
            raise Exception("Quantum hardware isn't defined")
        if not (issubclass(type(gate), Instruction)):
            raise Exception("Gate isn't Instruction type")
        if not force_connection and not self.quantum_hardware.qubit_connectivity.check_connection(connections):
            raise NoQubitConnectionError(connections, gate)
        gate_connection = GateConnection(self.quantum_hardware, gate, connections, cregs)
        self.chain.insert(position, gate_connection)
        self._matrix = None

    def delete_gate(self, gate_number):
        self.chain.pop(gate_number)
        self._matrix = None

    def extend(self, c, force_connection=False):
        """Extend GateChain object by appending elements from c"""
        for gate_connection in c:
            self.add_gate(
                gate_connection.gate,
                gate_connection.connections,
                gate_connection.cregs,
                force_connection=force_connection,
            )

    def strip_empty_qubits(self, num_qubits=None):
        """Strip empty qubits from the GateChain.
        Returns: (GateChain, remapping_dict).
        Stripped GateChain object has number of qubits equal to
        populated_qubits_cnt and qubit_connectivity respects connectivity of the original GateChain segment.
        Requires remapping of original qubit placement to a new placement.
        Remapping dictionary has following format {q_old: q_new}.
        Currently implemented a trivial remapping approach: first in - first out.
        """
        populated_qubits_cnt = 0
        seen_qubits = []
        for i in range(self.quantum_hardware.num_qubits):
            if self.get_num_gates_by_qubits(i) != 0:
                populated_qubits_cnt += 1
                seen_qubits.append(i)

        if num_qubits is not None:
            if populated_qubits_cnt > num_qubits:
                raise Exception(
                    f"num_qubits = {num_qubits} should be >= than populated_qubits_cnt = {populated_qubits_cnt}"
                )
            populated_qubits_cnt = num_qubits

        # Add some qubits to seen to prevent compressed circuit mapping error
        while len(seen_qubits) < populated_qubits_cnt:
            # Hack suitable only for line connectivity to fill voids
            for candidate in range(min(seen_qubits) + 1, max(seen_qubits)):
                if candidate not in seen_qubits:
                    if self.quantum_hardware.qubit_connectivity.is_connected_to_any(candidate, seen_qubits):
                        seen_qubits.append(candidate)
                        if len(seen_qubits) >= populated_qubits_cnt:
                            break

            if len(seen_qubits) >= populated_qubits_cnt:
                break

            for candidate in range(self.quantum_hardware.num_qubits):
                if candidate not in seen_qubits:
                    if self.quantum_hardware.qubit_connectivity.is_connected_to_any(candidate, seen_qubits):
                        seen_qubits.append(candidate)
                        if len(seen_qubits) >= populated_qubits_cnt:
                            break

        hw_name = "Stripped" + self.quantum_hardware.name
        gate_set = self.quantum_hardware.gate_set

        q_old = sorted(seen_qubits)
        q_new = list(range(populated_qubits_cnt))

        remapping_dict = dict(zip(q_old, q_new))

        qubit_connectivity = QubitConnectivity("stripped_connectivity", populated_qubits_cnt, connections_list=[])

        for q1 in q_old:
            for q2 in q_old:
                # Check if there is a connection in original hardware
                if (q1, q2) in self.quantum_hardware.qubit_connectivity.connections_list:
                    # Add connection for corresponding qubits in 'stripped' hardware
                    q1_new, q2_new = remapping_dict[q1], remapping_dict[q2]
                    qubit_connectivity.add_connection(q1_new, q2_new)

        stripped_hw = Hardware(
            name=hw_name, qubit_connectivity=qubit_connectivity, gate_set=gate_set
        )

        return self.remap_qubits(stripped_hw, remapping_dict), remapping_dict

    def remap_qubits(self, new_hardware, remapping_dict):
        new_chain = GateChain(new_hardware)
        for el in self.chain:
            g, old_conn = el.gate, el.connections
            new_conn = [remapping_dict[i] for i in old_conn]
            new_chain.add_gate(g, new_conn)

        return new_chain

    def dagger(self):
        """Daggered GateChain"""
        dagger_chain = GateChain(self.quantum_hardware)
        for el in reversed(self.chain):
            dagger_chain.add_gate(el.gate.dagger(), el.connections)
        return dagger_chain

    def shuffle_gates(self, seed=1):
        """GateChain with shuffled gates"""
        np.random.seed(seed)
        new_chain = GateChain(self.quantum_hardware)
        new_chain.chain = np.random.permutation(self.chain)
        return new_chain

    def cnot_parity_matrix(self):
        """Return Cnot parity matrix for Cnot-only GateChain"""
        for el in self.chain:
            assert el.gate.__class__.__name__ == 'Cnot', "Gate chain should consist of CNOTs only"
        num_qubits = self.quantum_hardware.num_qubits
        parity_m = np.eye(num_qubits, dtype=np.int64)
        for el in self.chain:
            g, conn = el.gate, el.connections
            cntrl, targ = conn[0], conn[1]
            parity_m[targ, :] = (parity_m[cntrl, :] + parity_m[targ, :]) % 2
        return parity_m

    def clifford_parity_matrix(self):
        """Return Clifford parity matrix for Clifford-only GateChain"""
        # Clifford circuit compressed representation, see https://arxiv.org/pdf/1305.0810.pdf
        n = self.quantum_hardware.num_qubits
        parity_m = np.eye(2 * n, dtype=np.int64)

        for el in self.chain:
            g, conn = el.gate, el.connections
            g_name = g.__class__.__name__
            if g_name == "Cnot":
                # Cnot(cntrl=i, targ=j) -> Add row i to row j, add row j+n to row i+n
                cntrl, targ = conn[0], conn[1]
                parity_m[targ, :] = (parity_m[cntrl, :] + parity_m[targ, :]) % 2
                parity_m[cntrl + n, :] = (parity_m[cntrl + n, :] + parity_m[targ + n, :]) % 2
            elif g_name == "H":
                # H(i) -> Exchange rows i and i+num_qubits
                i = conn[0]
                row1 = parity_m[i]
                row2 = parity_m[i + n]
                parity_m[i] = row2
                parity_m[i + n] = row1
            elif g_name == "S" or "Sd":
                # S(i) -> Add row i to row i+num_qubits
                i = conn[0]
                parity_m[i + n] = (parity_m[i] + parity_m[i + n]) % 2
            else:
                raise ValueError('Gate chain should consist of Clifford gates (Cnot, H, S)')
        return parity_m

    # Calculating gate_chain unitary matrix using tensor contraction.
    # The code in _add_unitary(...), _einsum_vecmul_index, _einsum_matmul_index_helper(..)
    # is based on Qiskit's code, see
    # qiskit-terra/qiskit/providers/basicaer/statevector_simulator.py.
    # Modifications include: (1) modified Qiskit's code to implement Einstein
    # index summation for matrix multiplication instead of vector-matrix multiplication;
    # (2) added option for matrix multiplication in reverse order (reverse_order).
    #
    # Original code is licensed as stated below:
    #
    # (C) Copyright IBM 2017, 2018.
    #
    # This code is licensed under the Apache License, Version 2.0. You may
    # obtain a copy of this license in the LICENSE.txt file in the root directory
    # of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
    #
    # Any modifications or derivative works of this code must retain this
    # copyright notice, and modified files need to carry a notice indicating
    # that they have been altered from the originals.
    def _einsum_vecmul_index(self, gate_indices, number_of_qubits, reverse_order=False):
        """Return the index string for Numpy.einsum matrix-vector multiplication.
        The returned indices are to perform a matrix multiplication A.v where
        the matrix A is an M-qubit matrix, vector v is an N-qubit vector, and
        M <= N, and identity matrices are implied on the subsystems where A has no
        support on v.
        Args:
            gate_indices (list[int]): the indices of the right matrix subsystems
                                      to contract with the left matrix.
            number_of_qubits (int): the total number of qubits for the right matrix.
            reverse_order (bool): if True, corresponds to tensor multiplication
                                  in reverse order
        Returns:
            str: An indices string for the Numpy.einsum function.
        """

        mat_l, mat_r, tens_lin, tens_lout = self._einsum_matmul_index_helper(
            gate_indices, number_of_qubits, reverse_order=reverse_order
        )
        # Swap indexes of left and right tensors
        # (equivalent to tensor multiplication in reverse order)
        if reverse_order:
            mat_l, mat_r = mat_r, mat_l
        # Combine indices into matrix multiplication string format
        # for numpy.einsum function
        indx = "{mat_l}{mat_r}, ".format(mat_l=mat_l, mat_r=mat_r) + "{tens_lin}...->{tens_lout}...".format(
            tens_lin=tens_lin, tens_lout=tens_lout
        )
        return indx

    def _einsum_matmul_index_helper(self, gate_indices, number_of_qubits, reverse_order=False):
        """Return the index string for Numpy.einsum matrix multiplication.
        The returned indices are to perform a matrix multiplication A.v where
        the matrix A is an M-qubit matrix, matrix v is an N-qubit vector, and
        M <= N, and identity matrices are implied on the subsystems where A has no
        support on v.
        Args:
            gate_indices (list[int]): the indices of the right matrix subsystems
                                       to contract with the left matrix.
            number_of_qubits (int): the total number of qubits for the right matrix.
        Returns:
            tuple: (mat_left, mat_right, tens_in, tens_out) of index strings for
            that may be combined into a Numpy.einsum function string.
        Raises:
            QiskitError: if the total number of qubits plus the number of
            contracted indices is greater than 26.
        """
        # Since we use ASCII alphabet for einsum index labels we are limited
        # to 26 total free left (lowercase) and 26 right (uppercase) indexes.
        # The rank of the contracted tensor reduces this as we need to use that
        # many characters for the contracted indices
        if len(gate_indices) + number_of_qubits > 26:
            raise ValueError("Total number of free indexes limited to 26")

        # Indices for N-qubit input tensor
        tens_in = ascii_lowercase[:number_of_qubits]

        # Indices for the N-qubit output tensor
        tens_out = list(tens_in)

        # Left and right indices for the M-qubit multiplying tensor
        mat_left = ""
        mat_right = ""

        # Update left indices for mat and output
        for pos, idx in enumerate(reversed(gate_indices)):
            mat_left += ascii_lowercase[-1 - pos]
            mat_right += tens_in[-1 - idx]
            tens_out[-1 - idx] = ascii_lowercase[-1 - pos]
        tens_out = "".join(tens_out)
        # Combine indices into matrix multiplication string format
        # for numpy.einsum function
        return mat_left, mat_right, tens_in, tens_out

    def _add_unitary(self, gate, qubits, matrix, reverse_order=False):
        """Apply an N-qubit unitary matrix.
        Args:
            gate (matrix_like): an N-qubit unitary matrix
            qubits (list): the list of N-qubits to apply gate on.
        """
        # If Instruction do not recalculate matrix
        if not isinstance(gate, Gate):
            return matrix
        # Get the number of qubits
        qubits = list(reversed(qubits))
        num_qubs_gate = len(qubits)
        num_qubits = self.quantum_hardware.num_qubits
        # Compute einsum index string for 1-qubit matrix multiplication
        indexes = self._einsum_vecmul_index(qubits, num_qubits, reverse_order=reverse_order)
        # Convert to complex rank-2N tensor
        gate_tensor = np.reshape(np.array(gate._u, dtype=complex), num_qubs_gate * [2, 2])
        # Reshape original matrix to a tensor form
        matrix = matrix.reshape([2, 2] * num_qubits)
        # Apply matrix multiplication
        u = np.einsum(indexes, gate_tensor, matrix, dtype=complex, casting="no").reshape(
            (2 ** num_qubits, 2 ** num_qubits)
        )
        return u

    def add_qreg_mapping(self, qreg_name, qreg_size):
        if qreg_name in self.qreg_mapping:
            raise ValueError(f"Error: Qreg name {qreg_name} already exists")

        start_qbit = sum([len(r) for r in self.qreg_mapping.values()])
        if start_qbit + qreg_size > self.quantum_hardware.num_qubits:
            raise ValueError(f"Hardware can't fit qreg {qreg_name} with size {qreg_size}")
        self.qreg_mapping[qreg_name] = {v: v + start_qbit for v in range(qreg_size)}

    def add_creg_mapping(self, creg_name, creg_size):
        if creg_name in self.creg_mapping:
            raise ValueError(f"Error: Creg name {creg_name} already exists")
        start_cbit = sum([len(r) for r in self.creg_mapping.values()])
        if start_cbit + creg_size > self.quantum_hardware.num_cbits:
            raise ValueError(f"Hardware can't fit creg {creg_name} with size {creg_size}")
        self.creg_mapping[creg_name] = {v: v + start_cbit for v in range(creg_size)}

    def qreg_qubit_index(self, qreg_name, qreg_qubit):
        return self.qreg_mapping[qreg_name][qreg_qubit]

    def _add_virtual_swaps(self, matrix):
        """Add virtual Swap gates and recalculates unitary matrix corresponding to:
                (1) relabeling of input logical qubits due to mapping to physical qubits
                (2) reordering of output qubits due to reordering of measure gates
        Args:
            matrix: (np.array), cashed unitary matrix
        """
        # Get the number of qubits
        # (1) insert virtual Swap gates due to relabeling of input logical qubits due to mapping to physical qubits
        assert len(self.qreg_mapping) == 1, f"Only one quantum register is supported for fidelity calculation: detected {len(self.qreg_mapping)}"
        qreg_name = list(self.qreg_mapping.keys())[0]
        permutation = list(self.qreg_mapping[qreg_name].values())
        tmp_chain = GateChain(self.quantum_hardware)
        for (i, j) in reversed(Permutation(permutation).transpositions()):
            tmp_chain.add_gate(Swap(), [i, j], force_connection=True)  # TODO this operation doesn't check connectivity
        matrix_l = tmp_chain._calculate_matrix()

        # (2) insert virtual Swap gates due to reordering of measure gates
        creg_mapping = {}
        for el in self.chain:
            if isinstance(el.gate, Measure):
                creg_mapping[el.connections[0]] = el.cregs[0]
        tmp_chain = GateChain(self.quantum_hardware)
        permutation = [p[1] for p in sorted(creg_mapping.items(), key=lambda x: x[0])]

        # print('QASM!!!', self.to_qasm())

        for (i, j) in reversed(Permutation(permutation).transpositions()):
            tmp_chain.add_gate(Swap(), [i, j], force_connection=True)  # TODO this operation doesn't check connectivity

        matrix_r = tmp_chain._calculate_matrix()
        matrix = np.matmul(matrix_r, np.matmul(matrix, matrix_l))

        return matrix

    def _calculate_matrix(self):
        """Evaluate total unitary matrix of the circuit (gate chain).
        """
        number_of_qubits = self.quantum_hardware.num_qubits
        matrix = np.eye(2 ** number_of_qubits, dtype=np.complex128)

        for g in self.chain:
            matrix = self._add_unitary(g.gate, g.connections, matrix)
        return matrix

    def calculate_noise(self):
        if self.quantum_hardware is None:
            raise Exception("Quantum hardware isn't defined")
        return self.quantum_hardware.calculate_gate_chain_noise(self)

    def calculate_cost(self):
        if self.quantum_hardware is None:
            raise Exception("Quantum hardware isn't defined")
        return self.quantum_hardware.calculate_gate_chain_cost(self)

    def __len__(self):
        return len(self.chain)

    def print(self):
        print(str(self))

    def __str__(self):
        s = "[" + ", ".join([str(g) for g in self.chain]) + "]"
        return "Gate Chain " + s

    def find_subchain(self, subchain):
        raise Exception("find_subchain isn't defined")

    def get_depth(self):
        "Calculates depth of the gate chain by converting it to QiskitCircuit"
        # TODO: implement our own get_depth based on dag representation
        qiskit_circuit = self.convert_to(format_id="qiskit")
        depth = qiskit_circuit.depth()
        return depth

    def get_depth_qubit(self):
        if self.quantum_hardware is None:
            raise Exception("Quantum hardware isn't defined")
        depth = 0
        qubit = 0
        for q in range(self.quantum_hardware.num_qubits):
            if depth < self.get_num_gates_by_qubits(q):
                depth = self.get_num_gates_by_qubits(q)
                qubit = q
        return qubit

    def get_depth_by_gate_type(self, gate_names):
        """ Calculates depth by gate type
            Args:
                gate_names (List(str))
            List of gate names
            Returns:
                depth (int)
        """
        if self.quantum_hardware is None:
            raise Exception("Quantum hardware isn't defined")
        tmp_chain = GateChain(self.quantum_hardware)
        for el in self:
            g, conn, cregs = el.gate, el.connections, el.cregs
            if g.name in gate_names and isinstance(g, Gate):
                tmp_chain.add_gate(g, conn, cregs=cregs, force_connection=True)
        depth = tmp_chain.get_depth()
        return depth

    def get_num_gates(self):
        return self.__len__()

    def get_gate_count(self):
        if self.quantum_hardware is None:
            raise Exception("Quantum hardware isn't defined")
        gates = {}
        for conn in self.chain:
            g = conn._gate
            if g.name not in gates:
                gates[g.name] = 0
            gates[g.name] += 1
        return gates

    def get_n_qubit_gate_count(self, n):
        """ Calculates number of n-qubit gates in the gate chain, e.g.
        number of single qubit gates (n=1), two qubit gates (n=2), etc.
        """
        gate_count = len([gc._gate for gc in self.chain if gc._gate.num_qubits == n])
        return gate_count

    def delete_subchain(self, subchain):
        raise Exception("'delete_subchain' function isn't defined")

    def get_gate_count_by_gate_type(self, gate, gate_num=None):
        i = 0
        for g in islice(self.chain, 0, gate_num):
            if type(g.gate) is gate:
                i = i + 1
        return i

    def check_connectivity(self):
        """Check connectivity violations

        :return: list of connectivity violations
        """
        violations = [
            (indx, str(g))
            for indx, g in enumerate(self.chain)
            if not self.quantum_hardware.qubit_connectivity.check_connection(g.connections)
        ]
        return violations

    def check_gate_set(self):
        """ Check gate set violations
        :return: list of gate set violations
        """
        violations = [
            (indx, str(g.gate))
            for indx, g in enumerate(self.chain)
            if not any(isinstance(g.gate, t) for t in self.quantum_hardware.gate_set.gate_list)
        ]
        return violations

    def check_qubit_number(self):
        """
        :return: violations of gate number
        """
        violations = [
            (indx, str(g.gate))
            for indx, g in enumerate(self.chain)
            for con in g.connections if con > self.quantum_hardware.num_qubits
        ]
        return violations

    def get_num_gates_by_qubits(self, qubits):
        """ Get number of gates by qubit number

        :param qubits: qubit number or list of qubits
        :return:
        """
        return len(self.get_gates_by_qubits(qubits))

    def get_gates_by_qubits(self, qubits):
        return [
            g
            for g in self.chain
            if all(item in g.connections for item in (qubits if type(qubits) is list else [qubits]))
        ]

    def copy(self):
        c = GateChain(self.quantum_hardware)
        c.chain = copy(self.chain)
        if self._matrix is not None:
            c._matrix = self._matrix.copy()
        return c

    def save_chain(self, fname):
        with open(fname, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load_chain(self, fname):
        with open(fname, "rb") as f:
            gate_chain = pickle.load(fname)
        return gate_chain

    def to_qasm(self, qreg_name="q", creg_name="c"):
        s = "// Copyright (c) 2019 Turation Ltd\n" "\n" "OPENQASM 2.0;\n" 'include "qelib1.inc";\n'
        s += "\n" "qreg " + qreg_name + "[" + str(self.quantum_hardware.num_qubits) + "];" + "\n"
        s += "creg " + creg_name + "[" + str(self.quantum_hardware.num_qubits) + "];" "\n"
        gate_list = [g.to_qasm(qreg_name) for g in self.chain]
        s += "\n".join(gate_list)
        s += "\n"
        return s

    def save_to_qasm(self, output_dir, qreg_name="q", creg_name="c"):
        with open(output_dir, "w") as f:
            s = self.to_qasm(qreg_name=qreg_name, creg_name=creg_name)
            f.write(s)
        return True

    @staticmethod
    def from_qasm_list_of_lines(lines, quantum_hardware=None):
        return GateChain.from_qasm_string("\n".join(lines), quantum_hardware)

    @staticmethod
    def from_qasm_string(qasm_data, quantum_hardware=None, file_name=None):
        with QasmParser(file_name) as qasm_p:
            qasm_p.parse_debug(False)
            ast = qasm_p.parse(qasm_data)
            hardware_from_qasm = quantum_hardware is None
            if quantum_hardware is None:
                connectivity = All2All(0)
                quantum_hardware = Hardware(
                    f"FromQasm",
                    gate_set=GateSet(f"FromQasm", []),
                    qubit_connectivity=connectivity
                )
            # AstInterpreter can modify hardware, so we need to make a copy
            gate_chain = GateChain(quantum_hardware.copy())
            AstInterpreter(gate_chain, hardware_from_qasm)._process_node(ast)
            num_qubits = gate_chain.quantum_hardware.num_qubits

            return gate_chain

    @staticmethod
    def from_qasm(input_file, quantum_hardware=None):
        with open(input_file, mode="r", encoding="utf-8-sig") as f:
            qasm_data = f.read()

            return GateChain.from_qasm_string(qasm_data, quantum_hardware, file_name=input_file)

    @staticmethod
    def string_to_angle(string):
        r"""Convert string into angle
        """
        if string.find("pi") == -1:
            return float(string)
        else:
            values = string.split("/")
            if len(values) == 2:
                num = values[0]
                den = values[1]
                den = float(den)
                numbers = num.split("*")
                if len(numbers) == 2:
                    if numbers[0].find("pi") == -1:
                        n0 = numbers[0]
                    else:
                        n0 = numbers[1]
                    return float(n0) * np.pi / den
                else:
                    if numbers[0].find("-") == -1:
                        return np.pi / den
                    else:
                        return -np.pi / den
            else:
                numbers = values[0].split("*")
                if len(numbers) == 2:
                    if numbers[0].find("pi") == -1:
                        n0 = numbers[0]
                    else:
                        n0 = numbers[1]
                    return float(n0) * np.pi
                else:
                    if numbers[0].find("-") == -1:
                        return np.pi
                    else:
                        return -np.pi

    converters = {}

    @classmethod
    def convert_from(cls, circuit_object, format_id, **kwargs):
        """Creates GateChain from another quantum framework circuit object
        :param circuit_object: Object to convert
        :param format_id: Format ID
        :type format_id: str
        """
        if format_id not in cls.converters:
            raise RuntimeError(f"Format ID {format_id} is not supported")

        return cls.converters[format_id].to_gate_chain(circuit_object, **kwargs)

    def convert_to(self, format_id, **kwargs):
        """Converts GateChain object to one of frameworks or formats
        :param format_id: Format ID
        :type format_id: str

        """
        if format_id not in self.converters:
            raise RuntimeError(f"Format ID {format_id} is not supported")

        return self.converters[format_id].from_gate_chain(self, **kwargs)

    @classmethod
    def register_converter(cls, converter_class):
        """Register class to perform gate chain conversion
        :param converter_class: Converter class
        :type converter_class: GateChainConverter
        """
        cls.converters[converter_class.format_id] = converter_class


class AstInterpreter:
    """Interprets an OpenQASM by expanding subroutines and unrolling loops
    """

    # This class code is Based on Qiskit AstInterpreter qiskit-terra/qiskit/converters/ast_to_dag.py
    #
    # Original code is licensed as stated below:
    #
    # (C) Copyright IBM 2017, 2018.
    #
    # This code is licensed under the Apache License, Version 2.0. You may
    # obtain a copy of this license in the LICENSE.txt file in the root directory
    # of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
    #
    # Any modifications or derivative works of this code must retain this
    # copyright notice, and modified files need to carry a notice indicating
    # that they have been altered from the originals.

    def __init__(self, gate_chain, hardware_from_qasm):
        """Initialize interpreter's data."""
        # Gate Chain object to populate
        self.gate_chain = gate_chain
        # OPENQASM version number (ignored for now)
        self.version = 0.0
        # Dict of gates names and properties
        self.gates = OrderedDict()
        # Keeping track of conditional gates
        self.condition = None
        # List of dictionaries mapping local parameter ids to expression Nodes
        self.arg_stack = [{}]
        # List of dictionaries mapping local bit ids to global ids (name, idx)
        self.bit_stack = [{}]
        self.hardware_from_qasm = hardware_from_qasm

    def _process_bit_id(self, node):
        """Process an Id or IndexedId node as a bit or register type

        Return a list of tuples (Register,index)
        """
        reg = None

        if node.name in self.gate_chain.qreg_mapping:
            reg = self.gate_chain.qreg_mapping[node.name]
        elif node.name in self.gate_chain.creg_mapping:
            reg = self.gate_chain.creg_mapping[node.name]

        if node.type == "indexed_id":
            # An indexed bit or qubit
            # return [self.gate_chain.quantum_hardware.qreg_qubit_index(node.name, node.index)]
            return [reg[node.index]]

        elif node.type == "id":
            # raise NotImplementedError()
            # # A qubit or qreg or creg
            if not self.bit_stack[-1]:
                # Global scope
                return list(reg)
            else:
                # local scope
                if node.name in self.bit_stack[-1]:
                    return [self.bit_stack[-1][node.name]]
                raise RuntimeError("expected local bit name:", "line=%s" % node.line, "file=%s" % node.file)
        return None

    def _process_custom_unitary(self, node):
        """Process a custom unitary node
        """
        name = node.name
        if node.arguments is not None:
            args = self._process_node(node.arguments)
        else:
            args = []
        bits = [self._process_bit_id(node_element) for node_element in node.bitlist.children]
        if name in self.gates:
            gargs = self.gates[name]["args"]
            gbits = self.gates[name]["bits"]
            # Loop over register arguments, if any.
            maxidx = max(map(len, bits))
            for idx in range(maxidx):
                self.arg_stack.append({gargs[j]: args[j] for j in range(len(gargs))})
                # Only index into register arguments.
                element = [idx * x for x in [len(bits[j]) > 1 for j in range(len(bits))]]
                self.bit_stack.append({gbits[j]: bits[j][element[j]] for j in range(len(gbits))})
                self._add_gate_chain_gate(
                    name, [self.arg_stack[-1][s].sym() for s in gargs], [self.bit_stack[-1][s] for s in gbits]
                )
                self.arg_stack.pop()
                self.bit_stack.pop()
        else:
            raise RuntimeError("Internal Error: Undefined gate:", "line=%s" % node.line, "file=%s" % node.file)

    def _process_gate(self, node, opaque=False):
        """Process a gate node

        If opaque is True, process the node as an opaque gate node
        """
        self.gates[node.name] = {}
        de_gate = self.gates[node.name]
        de_gate["print"] = True  # default
        de_gate["opaque"] = opaque
        de_gate["n_args"] = node.n_args()
        de_gate["n_bits"] = node.n_bits()
        if node.n_args() > 0:
            de_gate["args"] = [element.name for element in node.arguments.children]
        else:
            de_gate["args"] = []
        de_gate["bits"] = [c.name for c in node.bitlist.children]
        if node.name in self.gate_chain.quantum_hardware.gate_set.gates_by_qasm_name:
            return
        if opaque:
            de_gate["body"] = None
        else:
            de_gate["body"] = node.body

    def _process_cnot(self, node):
        """Process a CNOT gate node
        """
        id0 = self._process_bit_id(node.children[0])
        id1 = self._process_bit_id(node.children[1])
        if not (len(id0) == len(id1) or len(id0) == 1 or len(id1) == 1):
            raise RuntimeError("Internal Error: qreg size mismatch", "line=%s" % node.line, "file=%s" % node.file)
        maxidx = max([len(id0), len(id1)])
        for idx in range(maxidx):
            if len(id0) > 1 and len(id1) > 1:
                self.gate_chain.add_gate(Cnot(), [id0[idx], id1[idx]])
            elif len(id0) > 1:
                self.gate_chain.add_gate(Cnot(), [id0[idx], id1[0]])
            else:
                self.gate_chain.add_gate(Cnot(), [id0[0], id1[idx]])

    def _process_measure(self, node):
        """Process a measurement node."""

        id0 = self._process_bit_id(node.children[0])
        id1 = self._process_bit_id(node.children[1])

        if len(id0) != len(id1):
            raise QiskitError("Internal error: reg size mismatch", "line=%s" % node.line, "file=%s" % node.file)
        for idx, idy in zip(id0, id1):
            meas_gate = Measure()
            meas_gate.condition = None
            self.gate_chain.add_gate(meas_gate, connections=[idx], cregs=[idy])

    def _process_barrier(self, node):
        """Process a barrier node."""
        ids = self._process_node(node.children[0])
        qubits = []
        for qubit in ids:
            for j, _ in enumerate(qubit):
                qubits.append(qubit[j])
        self.gate_chain.add_gate(Barrier(), connections=qubits, cregs=[])

    def _process_if(self, node):
        """Process an if node"""
        raise NotImplementedError()

    def _process_children(self, node):
        """Call process_node for all children of node"""
        for kid in node.children:
            self._process_node(kid)

    def _process_node(self, node):
        """Carry out the action associated with a node"""
        if node.type == "program":
            self._process_children(node)

        elif node.type == "qreg":
            if self.hardware_from_qasm:
                self.gate_chain.quantum_hardware.num_qubits += node.index
                num_qubits = self.gate_chain.quantum_hardware.num_qubits
                self.gate_chain.quantum_hardware.qubit_connectivity = All2All(num_qubits)
                self.gate_chain.quantum_hardware.update_name()
            self.gate_chain.add_qreg_mapping(node.name, node.index)

        elif node.type == "creg":
            if self.hardware_from_qasm:
                self.gate_chain.quantum_hardware.num_cbits += node.index
            self.gate_chain.add_creg_mapping(node.name, node.index)

        elif node.type == "id":
            raise RuntimeError("Internal Error: _process_node on id")

        elif node.type == "int":
            raise RuntimeError("Internal Error: _process_node on int")

        elif node.type == "real":
            raise RuntimeError("Internal Error: _process_node on real")

        elif node.type == "indexed_id":
            raise RuntimeError("Internal Error: _process_node on indexed_id")

        elif node.type == "id_list":
            # We process id_list nodes when they are leaves of barriers.
            return [self._process_bit_id(node_children) for node_children in node.children]

        elif node.type == "primary_list":
            # We should only be called for a barrier.
            return [self._process_bit_id(m) for m in node.children]

        elif node.type == "gate":
            self._process_gate(node)

        elif node.type == "custom_unitary":
            self._process_custom_unitary(node)

        elif node.type == "universal_unitary":
            args = [x.sym() for x in self._process_node(node.children[0])]
            qid = self._process_bit_id(node.children[1])
            for element in qid:
                self.gate_chain.add_gate(U3(*args), qid)

        elif node.type == "cnot":
            self._process_cnot(node)

        elif node.type == "expression_list":
            return node.children

        elif node.type == "binop":
            raise RuntimeError("Internal Error: _process_node on binop")

        elif node.type == "prefix":
            raise RuntimeError("Internal Error: _process_node on prefix")

        elif node.type == "measure":
            self._process_measure(node)

        elif node.type == "format":
            self.version = node.version()

        elif node.type == "barrier":
            self._process_barrier(node)

        elif node.type == "reset":
            raise NotImplementedError()

        elif node.type == "if":
            self._process_if(node)

        elif node.type == "opaque":
            self._process_gate(node, opaque=True)

        elif node.type == "external":
            raise RuntimeError("Internal Error: _process_node on external")

        else:
            raise RuntimeError(
                "Internal Error: Undefined node type", node.type, "line=%s" % node.line, "file=%s" % node.file
            )
        return None

    def _add_gate_chain_gate(self, name, params, qargs):
        """
        Create a Gate Chain node out of a parsed AST op node

        Args:
            name (str): operation name to apply to the Gate Chain
            params (list): op parameters
            qargs (list(Qubit)): qubits to attach to
        """
        op = self._create_op(name, params)
        if not self.gate_chain.quantum_hardware.qubit_connectivity.check_connection(qargs) and self.hardware_from_qasm:
            # Fix connection
            if len(qargs) == 2:
                self.gate_chain.quantum_hardware.qubit_connectivity.add_connection(qargs[0], qargs[1])
                self.gate_chain.quantum_hardware.qubit_connectivity.add_connection(qargs[1], qargs[0])
            else:
                pass
        self.gate_chain.add_gate(op, qargs)

    def _create_op(self, name, params):
        if name in self.gate_chain.quantum_hardware.gate_set.gates_by_qasm_name:
            op = self.gate_chain.quantum_hardware.gate_set.gates_by_qasm_name[name](*params)
        elif self.hardware_from_qasm and name in qasm_gate_table_all:
            self.gate_chain.quantum_hardware.gate_set.gate_list.append(qasm_gate_table_all[name])
            op = self.gate_chain.quantum_hardware.gate_set.gates_by_qasm_name[name](*params)
        elif name in self.gates:
            raise NotImplementedError()
        else:
            raise RuntimeError("Unknown operation for last node name %s" % name)
        return op


from arline_quantum.gate_chain.converters import QiskitGateChainConverter, CirqGateChainConverter

GateChain.register_converter(QiskitGateChainConverter)
GateChain.register_converter(CirqGateChainConverter)
