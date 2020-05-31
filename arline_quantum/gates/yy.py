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


class Yy(Gate):
    r"""**Name:**
        :math:`YY\left(\phi\right)` gate

    **Description:**

        **Matrix:**

            .. math::

                \begin{bmatrix}
                    \cos(\phi)   &           0   &           0   & i \sin(\phi)\\
                    0            &    \cos(\phi) & -i \sin(\phi) &          0\\
                    0            & -i \sin(\phi) &    \cos(\phi) &          0\\
                    i  \sin(\phi)&           0   &           0   &   \cos(\phi)
                \end{bmatrix}

    :param phi: angle in radians
    :type phi: float
    """

    is_discrete = False  #: Flag for discrete or continuous
    num_qubits = 2  #: The number of qubits the gate acts on
    graph_symbols = ["IY", "IY"]  #: List of pseudo graph symbols

    def __init__(self, *args):
        r"""Create a new gate
        """
        super().__init__(*args)

    def calculate_u(self, args):
        r"""Calculate matrix
        """
        phi = args[0]
        y_pauli = np.array([[0, -1j], [1j, 0]], dtype=np.complex_)
        return linalg.expm(-1j * phi / 2.0 * np.kron(y_pauli, y_pauli))

    def conjugate(self):
        """ Produce conjugated gate

        :return: new dagger gate
        :rtype: Gate
        """
        return Yy(-self.args[0])

    def to_qasm(self):
        r"""Describes how the gate will be shown in OPENQASM format
        """
        angles = self.angles(representation='decimal')
        return "ryy" + "(" + ",".join([a for a in angles]) + ")"

    @staticmethod
    def to_qiskit_name():
        r"""Convert to Qiskit gate name
        """
        return "ryy"
