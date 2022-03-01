# Arline Quantum
# Copyright (C) 2019-2022 Turation Ltd
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


def matrix_to_psi(matrix_u):
    """ Calculate statevector for qubits initialised in state |0>"""
    # Equivalent to psi = np.dot(matrix_u, psi0),
    # where psi0 = [1, 0]^\otimes(num_qubits)
    return matrix_u[:, 0]


def statevector_fidelity(target_psi, current_psi):  #TODO qsp_fidelity -> statevector_fidelity
    """Fidelity (abs) between the current_psi state and the target_psi gate chains"""
    fid = np.abs(np.dot(current_psi, target_psi.conjugate()))
    return fid


def unitary_fidelity(target_u, current_u):  #TODO decompose_fidelity -> unitary_fidelity
    """Fidelity (abs) between the current_u state and the target_u gate chains"""
    fid = np.abs(np.trace(np.matmul(current_u, np.matrix(target_u).H))) / len(current_u)
    return fid


def meas_fidelity(target_psi, current_psi):
    """Similarity metric between statevectors in the presence of measurements"""
    fid = np.dot(np.abs(target_psi), np.abs(current_psi))
    return fid
