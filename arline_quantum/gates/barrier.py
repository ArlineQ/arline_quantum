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


from arline_quantum.gates.instruction import Instruction


class Barrier(Instruction):
    r"""**Name:**
        :math:`Barrier` Instruction

    **Description:**

        The :math:`Barrier` gate separates different parts of quantum circuit

    """

    num_qubits = 1  #: The number of qubits the gate acts on
    num_cregs = 1  #: The number of classical bits to be measured
    graph_symbols = ["B"]  #: List of pseudo graph symbols

    def __init__(self, qreg_name='q', *args):
        r"""Create a new measurement gate
        """
        super().__init__(*args)
        # fmt: off

    def to_qasm(self):
        r"""Describes how the gate will be shown in OPENQASM format.
        """
        return "barrier"

    @staticmethod
    def args_to_str(*args):
        r"""Describes how the barrier parameters will be shown.
        """
        return ""

    @staticmethod
    def to_qiskit_name():
        r"""Convert to Qiskit gate name.
        """
        return "barrier"
