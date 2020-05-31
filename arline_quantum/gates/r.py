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


class R(Gate):
    r"""**Name:**
        :math:`R\left(\theta, \phi\right)` Gate

    **Description:**

        .. math::
            R(\theta, 0) = R_X(\theta), R(\theta, \pi/2) = R_Y(\theta)

        **Matrix:**

            .. math::

                \begin{bmatrix}
                    \cos(\theta/2) & -i \cdot e^{-i \phi} \cdot \sin(\theta/2)\\
                    -i \cdot e^{i \phi} \cdot \sin(\theta/2) & \cos(\theta/2)
                \end{bmatrix}

    :param theta: angle in radians
    :type theta: float
    :param phi: angle in radians
    :type phi: float
    """

    is_discrete = False  #: Flag for discrete or continuous
    num_qubits = 1  #: The number of qubits the gate acts on
    graph_symbols = ["R"]  #: List of pseudo graph symbols

    def __init__(self, *args):
        r"""Create a new gate
        """
        super().__init__(*args)

    def calculate_u(self, args):
        r"""Calculate matrix
        """
        theta = args[0]
        phi = args[1]
        return np.array(
            [
                [np.cos(theta / 2), -1j * np.exp(-1j * phi) * np.sin(theta / 2)],
                [-1j * np.exp(1j * phi) * np.sin(theta / 2), np.cos(theta / 2)],
            ],
            dtype=np.complex_,
        )

    def conjugate(self):
        """ Produce conjugated gate

        :return: new dagger gate
        :rtype: Gate
        """
        return R(-self.args[0], self.args[1])

    def to_qasm(self):
        r"""Describes how the gate will be shown in OPENQASM format
        """
        angles = self.angles(representation='decimal')
        return "r" + "(" + ",".join([a for a in angles]) + ")"

    @staticmethod
    def to_qiskit_name():
        r"""Convert to Qiskit gate name
        """
        return "r"
