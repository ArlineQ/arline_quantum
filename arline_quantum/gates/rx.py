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
from scipy import linalg

from arline_quantum.gates.gate import Gate


class Rx(Gate):
    r"""**Name:**
        :math:`R_X\left(\theta\right)` Gate

    **Description:**

        The :math:`R_X(\theta)` gate is a single-qubit rotation through angle :math:`\theta` (radians) around the x-axis

        **Matrix:**

        .. math::
            \begin{bmatrix}
                \cos(\theta/2) & -i \sin(\theta/2) \\
                -i \sin(\theta/2) & \cos(\theta/2)
            \end{bmatrix}



    :param theta: angle in radians
    :type theta: float
    """

    is_discrete = False  #: Flag for discrete or continuous
    num_qubits = 1  #: The number of qubits the gate acts on
    graph_symbols = ["RX"]  #: List of pseudo graph symbols

    def __init__(self, *args):
        r"""Create a new gate
        """
        super().__init__(*args)

    def calculate_u(self, args):
        r"""Calculate matrix
        """
        theta = self._args[0]
        x_pauli = np.array([[0, 1], [1, 0]], dtype=np.complex_)
        return linalg.expm(-1j * theta / 2.0 * x_pauli)

    def conjugate(self):
        """ Produce conjugated gate

        :return: new dagger gate
        :rtype: Gate
        """
        return Rx(-self.args[0])

    def to_qasm(self):
        r"""Describes how the gate will be shown in OPENQASM format
        """
        angles = self.angles(representation='decimal')
        return "rx" + "(" + ",".join([a for a in angles]) + ")"

    @staticmethod
    def to_qiskit_name():
        r"""Convert to Qiskit gate name
        """
        return "rx"
