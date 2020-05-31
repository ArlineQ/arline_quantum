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


class Cu1(Gate):
    r"""**Name:**
        :math:`CU_{1}\left(\lambda\right)` Gate

    **Description:**

        The :math:`CU_{1}\left(\lambda\right)` gate is a controlled :math:`U_1` rotation with 1 angle :math:`\lambda`
        (radians)

        **Other names:**
            Controlled :math:`U_1` gate

        **Matrix:**

            This matrix representation corresponds to [target_qubit, control_qubit]

            .. math::

                \begin{bmatrix}
                    1 & 0 & 0 & 0\\
                    0 & 1 & 0 & 0\\
                    0 & 0 & 1 & 0 \\
                    0 & 0 & 0 & \exp(i\lambda)
                \end{bmatrix}

    :param lambda: angle in radians
    :type lambda: float
    """

    is_discrete = False  #: Flag for discrete or continuous
    num_qubits = 2  #: The number of qubits the gate acts on
    graph_symbols = [".", "U1"]  #: List of pseudo graph symbols

    def __init__(self, *args):
        r"""Create a new gate
        """
        super().__init__(*args)

    def calculate_u(self, args):
        r"""Calculate matrix
        """
        lam = args[0]
        p0 = np.array([[1, 0], [0, 0]])
        p1 = np.array([[0, 0], [0, 1]])
        identity = np.eye(2)
        # fmt: off
        u1 = np.array([[1, 0], [0, np.exp(1j * lam)]], dtype=complex)
        # fmt: on
        return np.kron(p0, identity) + np.kron(p1, u1)

    def conjugate(self):
        """ Produce conjugated gate

        :return: new dagger gate
        :rtype: Gate
        """
        return Cu1(-self.args[0])

    @staticmethod
    def to_qiskit_name():
        r"""Convert to Qiskit gate name
        """
        return "cu1"

    def to_qasm(self):
        r"""Describes how the gate will be shown in OPENQASM format
        """
        angles = self.angles(representation='decimal')
        return "cu1" + "(" + ",".join([a for a in angles]) + ")"
