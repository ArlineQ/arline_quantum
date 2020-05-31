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


class Rz(Gate):
    r"""**Name:**
        :math:`R_Z\left(\phi\right)` Gate

    **Description:**

        The :math:`R_Z(\phi)` gate is a single-qubit rotation through angle :math:`\phi` (radians) around the z-axis

        **Matrix:**

        .. math::

            \begin{bmatrix}
                1 & 0 \\
                0 & \exp\left(i \cdot \phi \right)
            \end{bmatrix}

    :param phi: angle in radians
    :type phi: float
    """

    is_discrete = False  #: Flag for discrete or continuous
    num_qubits = 1  #: The number of qubits the gate acts on
    graph_symbols = ["RZ"]  #: List of pseudo graph symbols

    def __init__(self, *args):
        r"""Create a new gate
        """
        super().__init__(*args)

    def calculate_u(self, args):
        r"""Calculate matrix
        """
        phi = self._args[0]
        return np.array([[1, 0], [0, np.exp(1j * phi)]], dtype=np.complex_)

    def to_qasm(self):
        r"""Describes how the gate will be shown in OPENQASM format
        """
        angles = self.angles(representation='decimal')
        return "rz" + "(" + ",".join([a for a in angles]) + ")"

    @staticmethod
    def to_qiskit_name():
        r"""Convert to Qiskit gate name
        """
        return "rz"
