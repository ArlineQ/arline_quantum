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
import types

from fractions import Fraction
from copy import copy


class Instruction:
    """An abstract quantum instruction class
    """

    num_qubits = None  #: The number of qubits the gate acts on
    graph_symbols = None  #: List of pseudo graph symbols
    num_cregs = None  # Number of classical registers

    def __init__(self, *args):
        self.args = args

    @property
    def args(self):
        """Get new args

        :return: gate args
        :rtype: list
        """
        return copy(self._args)

    @args.setter
    def args(self, args):
        self._args = args

    def __str__(self):
        return str(self.__class__.__name__) + self.args_to_str(*self._args)

    @staticmethod
    def args_to_str(*args):
        r"""Describes how the instruction paramaters will be shown.
        """
        raise NotImplementedError()

    @staticmethod
    def format_args(*args):
        r"""Convert args into list of strings.
        """
        raise NotImplementedError()

    def to_qasm(self, *args):
        r"""Describes how the gate will be shown in OPENQASM format.
        """
        return NotImplementedError()

    @staticmethod
    def to_qiskit_name():
        r"""Convert to Qiskit gate name.
        """
        return NotImplementedError()

    @property
    def name(self):
        return self.__class__.__name__
