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

from arline_quantum.gates.gate import Gate


class Cz(Gate):
    r"""**Name:**
        :math:`CZ` Gate

    **Description:**

        Controlled discrete two-qubit gate

        **Other names:**
            Controlled :math:`Z`

        **Matrix:**

            his matrix representation corresponds to [target_qubit, control_qubit]

            .. math::

                \begin{bmatrix}
                    1 & 0 & 0 &  0\\
                    0 & 1 & 0 &  0\\
                    0 & 0 & 1 &  0\\
                    0 & 0 & 0 & -1
                \end{bmatrix}

        **Inverse:**
            :math:`CZ^\dagger = CZ`
    """

    is_discrete = True  #: Flag for discrete or continuous
    num_qubits = 2  #: The number of qubits the gate acts on
    graph_symbols = [".", "Z"]  #: List of pseudo graph symbols

    def __init__(self, *args):
        r"""Create a new gate
        """
        super().__init__(*args)
        # fmt: off

    def calculate_u(self, args):
        r"""Calculate matrix
        """
        return np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, -1]
            ],
            dtype=np.complex_
        )
        # fmt: on

    def to_qasm(self):
        r"""Describes how the gate will be shown in OPENQASM format
        """
        return "cz"

    @staticmethod
    def to_qiskit_name():
        r"""Convert to Qiskit gate name
        """
        return "cz"
