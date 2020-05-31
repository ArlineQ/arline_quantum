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


class Cry(Gate):
    r"""**Name:**
        :math:`CR_Y\left(\theta\right)` Gate

    **Description:**

        Controlled continuous two-qubit gate

        The :math:`CR_Y(\theta)` gate is a controlled :math:`R_Y` rotation with angle :math:`\theta` (radians)

        **Other names:**
            Controlled :math:`R_Y` gate


        **Matrix:**

            This matrix representation corresponds to [target_qubit, control_qubit]

        .. math::

            \begin{bmatrix}
                1 & 0 & 0 & 0\\
                0 & 1 & 0 & 0\\
                0 & 0 & \cos(\theta/2) & -\sin(\theta/2) \\
                0 & 0 & \sin(\theta/2) &  \cos(\theta/2)
            \end{bmatrix}

    :param theta: angle in radians
    :type theta: float
    """

    is_discrete = False  #: Flag for discrete or continuous
    num_qubits = 2  #: The number of qubits the gate acts on
    graph_symbols = [".", "RY"]  #: List of pseudo graph symbols

    def __init__(self, *args):
        r"""Create a new gate
        """
        super().__init__(*args)

    def calculate_u(self, args):
        r"""Calculate matrix
        """
        theta = args[0]
        p0 = np.array([[1, 0], [0, 0]])
        p1 = np.array([[0, 0], [0, 1]])
        identity = np.eye(2)
        # fmt: off
        ry = np.array(
            [
                [np.cos(theta / 2), -np.sin(theta / 2)],
                [np.sin(theta / 2), np.cos(theta / 2)]
            ],
            dtype=np.complex_
        )
        # fmt: on
        return np.kron(p0, identity) + np.kron(p1, ry)

    def conjugate(self):
        """ Produce conjugated gate

        :return: new dagger gate
        :rtype: Gate
        """
        return Cry(-self.args[0])

    def to_qasm(self):
        r"""Describes how the gate will be shown in OPENQASM format
        """
        angles = self.angles(representation='decimal')
        return "cry" + "(" + ",".join([a for a in angles]) + ")"

    @staticmethod
    def to_qiskit_name():
        r"""Convert to Qiskit gate name
        """
        return "cry"
