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


class Y(Gate):
    r"""**Name:**
        :math:`Y` gate

    **Description:**

        **Other names:**
            Pauli :math:`Y`, Sigma :math:`Y`

        **Matrix:**

            .. math::

                \begin{bmatrix}
                    0 & -i\\
                    i &  0
                \end{bmatrix}

        **Inverse:**
            :math:`Y^\dagger = Y`
    """

    is_discrete = True  #: Flag for discrete or continuous
    num_qubits = 1  #: The number of qubits the gate acts on
    graph_symbols = ["Y"]  #: List of pseudo graph symbols

    def __init__(self, *args):
        """Create a new gate
        """
        super().__init__(*args)
        # fmt: off

    def calculate_u(self, args):
        r"""Calculate matrix
        """
        return np.array(
            [
                [0, -1j],
                [1j, 0]
            ],
            dtype=np.complex_
        )
        # fmt: on

    def to_qasm(self):
        r"""Describes how the gate will be shown in OPENQASM format
        """
        return "y"

    @staticmethod
    def to_qiskit_name():
        r"""Convert to Qiskit gate name
        """
        return "y"
