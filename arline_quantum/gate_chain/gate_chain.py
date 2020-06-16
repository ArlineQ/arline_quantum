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

import numpy as np

from arline_quantum.qasm_parser.qasmparser import QasmParser
from arline_quantum.gates import qasm_gate_table as qasm_gate_table_all
from arline_quantum.gates.cnot import Cnot
from arline_quantum.gates.gate import Gate
from arline_quantum.gates.u3 import U3
from arline_quantum.gate_sets.gate_set import GateSet
from arline_quantum.hardware.hardware import Hardware
from arline_quantum.gate_chain.gate_connection import GateConnection
from arline_quantum.qubit_connectivity.qubit_connectivity import All2All
from string import ascii_uppercase, ascii_lowercase


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
        # for i in range(1, self.num_qubits + self.num_qubits - 1):
        #     string_labels = []
        #     if i % 2 == 1:
        #         string_labels.append('-')
        #     else:
        #         string_labels.append(' ')
        #     self.chain_labels.append(string_labels)

    @property
    def matrix(self):
        """Calculate unitary matrix corresponding to the gate chain.
        Supports lazy matrix calculation, the call of self.matrix
        will result in recalculation of cashed unitary U = self._matrix.
        In order to update the cashed unitary after new gates were added to the
        gate chain we first evaluate the unitary of the appended gates U_new_gates.
        Then the resulting cashed unitary is the product U_new_gates * U or U * U_new_gates
        depending on wheather the new gates were appended
        to the beggining or end of the gate chain.
        """
        num_qubits = self.quantum_hardware.num_qubits
        if self.quantum_hardware is None:
            raise Exception("Quantum hardware isn't defined")
        if self._matrix is not None and 2 ** self.quantum_hardware.num_qubits != self._matrix.shape[0]:
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
            # The code is commented out because it contains an error
            # and fails test_reverse_matrix_building_order test.
            #
            # self._matrix = self._matrix.reshape(num_qubits * [2, 2])
            # reversed_subchain = reversed(list(islice(self.chain, 0, self._new_gates_cnt_left)))
            # for gate_connection in reversed_subchain:
            #     self._matrix = self._add_unitary(gate_connection.gate,
            #                                      gate_connection.connections,
            #                                      self._matrix,
            #                                      reverse_order=True)
            # self._matrix = self._matrix.reshape((2**num_qubits, 2**num_qubits))
            # self._new_gates_cnt_left = 0
            left_m = np.eye(2 ** self.quantum_hardware.num_qubits, dtype=np.complex_)
            left_m = left_m.reshape(num_qubits * [2, 2])
            for gate_connection in islice(self.chain, 0, self._new_gates_cnt_left):
                left_m = self._add_unitary(gate_connection.gate, gate_connection.connections, left_m)
            left_m = left_m.reshape((2 ** num_qubits, 2 ** num_qubits))
            self._matrix = np.matmul(self._matrix, left_m)
            self._new_gates_cnt_left = 0
        if self._new_gates_cnt_right > 0:
            self._matrix = self._matrix.reshape(num_qubits * [2, 2])
            for gate_connection in islice(self.chain, len(self.chain) - self._new_gates_cnt_right, len(self.chain)):
                self._matrix = self._add_unitary(gate_connection.gate, gate_connection.connections, self._matrix)
            self._matrix = self._matrix.reshape(2 ** num_qubits, 2 ** num_qubits)
            self._new_gates_cnt_right = 0

        return self._matrix

    def add_gate(self, gate, connections, force_connection=False):
        """Place gate to circuit

        :param gate: gate object
        :type gate: Gate
        :param connections: qubits to place the gate
        :type connections: tuple
        :param force_connection: don't check qubit connection
        :type force_connection: bool

        :raises NoQubitConnectionError: when there is no connection between qubits
        """
        if self.quantum_hardware is None:
            raise Exception("Quantum hardware isn't defined")
        if not (issubclass(type(gate), Gate)):
            raise Exception("Gate isn't gate type")
        if not force_connection and not self.quantum_hardware.qubit_connectivity.check_connection(connections):
            raise NoQubitConnectionError(connections, gate)
        gate_connection = GateConnection(self.quantum_hardware, gate, connections)
        self.chain.append(gate_connection)
        self._new_gates_cnt_right += 1

    def add_gate_left(self, gate, connections, force_connection=False):
        """Place gate to left end of the circuit

        :param gate: gate object
        :type gate: Gate
        :param connections: qubits to place the gate
        :type connections: tuple
        :param force_connection: don't check qubit connection
        :type force_connection: bool

        :raises NoQubitConnectionError: when there is no connection between qubits
        """
        if self.quantum_hardware is None:
            raise Exception("Quantum hardware is not set")
        if not (issubclass(type(gate), Gate)):
            raise Exception("Gate isn't Gate type")
        if not force_connection and not self.quantum_hardware.qubit_connectivity.check_connection(connections):
            raise NoQubitConnectionError(connections, gate)
        gate_connection = GateConnection(self.quantum_hardware, gate, connections)
        self.chain.appendleft(gate_connection)
        # self.noise = self.calculate_noise()
        self._new_gates_cnt_left += 1

    def insert_gate(self, gate, connections, position, force_connection=False):
        """Place gate at a given position

        :param gate: gate object
        :type gate: Gate
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
        if not (issubclass(type(gate), Gate)):
            raise Exception("Gate isn't gate type")
        if not force_connection and not self.quantum_hardware.qubit_connectivity.check_connection(connections):
            raise NoQubitConnectionError(connections, gate)
        gate_connection = GateConnection(self.quantum_hardware, gate, connections)
        self.chain.insert(position, gate_connection)
        self._matrix = None

    def delete_gate(self, gate_number):
        self.chain.pop(gate_number)
        self._matrix = None

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

        mat_l, mat_r, tens_lin, tens_lout = self._einsum_matmul_index_helper(gate_indices, number_of_qubits)
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

    def _einsum_matmul_index_helper(self, gate_indices, number_of_qubits):
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
        # Get the number of qubits
        qubits = list(reversed(qubits))
        num_qubs_gate = len(qubits)
        number_of_qubits = self.quantum_hardware.num_qubits
        # Compute einsum index string for 1-qubit matrix multiplication
        indexes = self._einsum_vecmul_index(qubits, number_of_qubits, reverse_order=reverse_order)
        # Convert to complex rank-2N tensor
        gate_tensor = np.reshape(np.array(gate._u, dtype=complex), num_qubs_gate * [2, 2])
        # Apply matrix multiplication
        u = np.einsum(indexes, gate_tensor, matrix, dtype=complex, casting="no")
        return u

    def _calculate_matrix(self):
        """Evaluate total unitary matrix of the circuit (gate chain).
        """
        number_of_qubits = self.quantum_hardware.num_qubits
        matrix = np.eye(2 ** number_of_qubits, dtype=np.complex128)
        matrix = matrix.reshape(number_of_qubits * [2, 2])

        for g in self.chain:
            qubits = g.connections
            matrix = self._add_unitary(g, qubits, matrix)
        matrix = matrix.reshape(2 ** number_of_qubits, 2 ** number_of_qubits)
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

    def load_chain(self, file):
        raise Exception("load_chain isn't defined")

    def save_chain(self, file):
        raise Exception("save_chain isn't defined")

    def find_subchain(self, subchain):
        raise Exception("find_subchain isn't defined")

    def add_subchain(self, subchain):
        raise Exception("add_subchain isn't defined")

    def get_depth(self):
        if self.quantum_hardware is None:
            raise Exception("Quantum hardware isn't defined")
        length = 0
        for q in range(self.quantum_hardware.num_qubits):
            if length < self.get_num_gates_by_qubit(q):
                length = self.get_num_gates_by_qubit(q)
        return length

    def get_depth_qubit(self):
        if self.quantum_hardware is None:
            raise Exception("Quantum hardware isn't defined")
        length = 0
        qubit = 0
        for q in range(self.quantum_hardware.num_qubits):
            if length < self.get_num_gates_by_qubit(q):
                length = self.get_num_gates_by_qubit(q)
                qubit = q
        return qubit

    def get_num_gates(self):
        return self.__len__()

    def get_gate_count(self):
        if self.quantum_hardware is None:
            raise Exception("Quantum hardware isn't defined")
        gates = {}
        for g in self.quantum_hardware.gate_set.gate_list:
            gates[g.__name__] = self.get_num_gates_by_gate_type(g)
        return gates

    def delete_subchain(self, subchain):
        raise Exception("'delete_subchain' function isn't defined")

    def get_num_gates_by_gate_type(self, gate, gate_num=None):
        i = 0
        for g in islice(self.chain, 0, gate_num):
            if type(g.gate) is gate:
                i = i + 1
        return i

    def get_num_gates_by_qubit(self, n):
        return len([g for g in self.chain if n in g.connections])

    def get_gates_by_qubit(self, n):
        return [g for g in self.chain if n in g.connections]

    def copy(self):
        c = GateChain(self.quantum_hardware)
        c.chain = copy(self.chain)
        if self._matrix is not None:
            c._matrix = self._matrix.copy()
        return c

    def to_qasm(self, qreg_name="q"):
        s = "// Copyright (c) 2019 Turation Ltd\n" "\n" "OPENQASM 2.0;\n" 'include "qelib1.inc";\n'
        s += "\n" "qreg " + qreg_name + "[" + str(self.quantum_hardware.num_qubits) + "];" + "\n" "\n"
        gate_list = [g.to_qasm(qreg_name) for g in self.chain]
        s += "\n".join(gate_list)
        s += "\n"
        return s

    def save_to_qasm(self, output_dir, qreg_name="q"):
        with open(output_dir, "w") as f:
            s = self.to_qasm(qreg_name=qreg_name)
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
                quantum_hardware = Hardware(f"FromQasm", num_qubits=0, gate_set=GateSet(f"FromQasm", []))
            # AstInterpreter can modufy hardware, so we need to make a copy
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

        if node.type == "indexed_id":
            # An indexed bit or qubit
            return [self.gate_chain.quantum_hardware.qreg_qubit_index(node.name, node.index)]
        elif node.type == "id":
            raise NotImplementedError()
            # # A qubit or qreg or creg
            # if not self.bit_stack[-1]:
            #     # Global scope
            #     return list(reg)
            # else:
            #     # local scope
            #     if node.name in self.bit_stack[-1]:
            #         return [self.bit_stack[-1][node.name]]
            #     raise RuntimeError("expected local bit name:", "line=%s" % node.line, "file=%s" % node.file)
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
        """Process a measurement node"""
        raise NotImplementedError()

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
            self.gate_chain.quantum_hardware.add_qreg_mapping(node.name, node.index)

        elif node.type == "creg":
            pass  # TODO creg is not implemented in gate chain

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
            raise NotImplementedError()

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
