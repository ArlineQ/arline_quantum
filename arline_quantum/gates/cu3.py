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


class Cu3(Gate):
    r"""**Name:**
        :math:`CU_{3}\left(\theta, \phi, \lambda\right)` Gate

    **Description:**

        Controlled continuous two-qubit gate

        The :math:`CU_{3}\left(\theta, \phi, \lambda\right)` gate is a controlled  :math:`U_3` rotation with 3 Euler
        angles :math:`\theta, \phi, \lambda` (radians)

        **Other names:**
            Controlled :math:`U_3` gate

        **Matrix:**

            This matrix representation corresponds to [target_qubit, control_qubit]

            .. math::

                \begin{bmatrix}
                    1 & 0 & 0 & 0\\
                    0 & 1 & 0 & 0\\
                    0 & 0 & \cos(\theta/2) & - \exp(i \lambda) \sin(\theta/2) \\
                    0 & 0 & \exp(i \phi) \sin(\theta/2) & \exp(i(\phi+\lambda)) \cos(\theta/2)
                \end{bmatrix}

    :param theta: angle in radians
    :type theta: float
    :param phi: angle in radians
    :type phi: float
    :param lambda: angle in radians
    :type lambda: float
    """

    is_discrete = False  #: Flag for discrete or continuous
    num_qubits = 2  #: The number of qubits the gate acts on
    graph_symbols = [".", "U3"]  #: List of pseudo graph symbols

    def __init__(self, *args):
        r"""Create a new gate
        """
        super().__init__(*args)

    def calculate_u(self, args):
        r"""Calculate matrix
        """
        theta = args[0]
        phi = args[1]
        lam = args[2]
        p0 = np.array([[1, 0], [0, 0]])
        p1 = np.array([[0, 0], [0, 1]])
        identity = np.eye(2)
        # fmt: off
        u3 = np.array(
            [
                [
                    np.cos(theta / 2), -np.exp(1j * lam) * np.sin(theta / 2)
                ],
                [
                    np.exp(1j * phi) * np.sin(theta / 2), np.exp(1j * (phi + lam)) * np.cos(theta / 2)
                ]
            ],
            dtype=complex)
        # fmt: on
        return np.kron(p0, identity) + np.kron(p1, u3)

    def conjugate(self):
        """ Produce conjugated gate

        :return: new dagger gate
        :rtype: Gate
        """
        return Cu3(-self.args[0], -self.args[1], -self.args[2])

    def to_qasm(self):
        r"""Describes how the gate will be shown in OPENQASM format
        """
        angles = self.angles(representation='decimal')
        return "cu3" + "(" + ",".join([a for a in angles]) + ")"

    @staticmethod
    def to_qiskit_name():
        r"""Convert to Qiskit gate name
        """
        return "cu3"
