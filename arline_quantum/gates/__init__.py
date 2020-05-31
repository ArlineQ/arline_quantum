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


import importlib
import re
from inspect import isclass

from sympy.parsing.sympy_parser import parse_expr

from arline_quantum.gates.ccnot import Ccnot
from arline_quantum.gates.ch import Ch
from arline_quantum.gates.cnot import Cnot
from arline_quantum.gates.crx import Crx
from arline_quantum.gates.cry import Cry
from arline_quantum.gates.crz import Crz
from arline_quantum.gates.cswap import Cswap
from arline_quantum.gates.cu1 import Cu1
from arline_quantum.gates.cu3 import Cu3
from arline_quantum.gates.cy import Cy
from arline_quantum.gates.cz import Cz
from arline_quantum.gates.gate import Gate
from arline_quantum.gates.h import H
from arline_quantum.gates.identity import I
from arline_quantum.gates.r import R
from arline_quantum.gates.rx import Rx
from arline_quantum.gates.ry import Ry
from arline_quantum.gates.rz import Rz
from arline_quantum.gates.s import S, Sd
from arline_quantum.gates.swap import Swap
from arline_quantum.gates.t import T, Td
from arline_quantum.gates.u1 import U1
from arline_quantum.gates.u2 import U2
from arline_quantum.gates.u3 import U3
from arline_quantum.gates.x import X
from arline_quantum.gates.xx import Xx
from arline_quantum.gates.y import Y
from arline_quantum.gates.yy import Yy
from arline_quantum.gates.z import Z
from arline_quantum.gates.zz import Zz

__all__ = [  # TODO update gates
    "ccnot",
    "ch",
    "cnot",
    "crx",
    "cry",
    "crz",
    "cswap",
    "cu1",
    "cu3",
    "cy",
    "cz",
    "h",
    "identity",
    "r",
    "rx",
    "ry",
    "rz",
    "s",
    "swap",
    "t",
    "u1",
    "u2",
    "u3",
    "x",
    "xx",
    "y",
    "yy",
    "z",
    "zz",
]

print("Loading gates names...")
__gates_by_names__ = {}

for f in __all__:
    m = importlib.import_module("arline_quantum.gates." + f)
    for v in dir(m):
        cl = getattr(m, v)
        if isclass(cl) and issubclass(cl, Gate):
            if cl == Gate:
                continue
            __gates_by_names__[cl.__name__] = cl


def gate_by_name(name):
    if "(" in name:
        # parse argument
        classname = re.sub(r"(.*)\(.*", r"\1", name)
        angles = re.sub(r".*\((.*)\)", r"\1", name)
        angles_f = [float(parse_expr(f)) for f in angles.split(",")]
        return __gates_by_names__[classname].make_discrete(*angles_f, class_name=name)
    return __gates_by_names__[name]


qasm_gate_table = {
    "u3": U3,
    "u2": U2,
    "u1": U1,
    "cx": Cnot,
    "id": I,
    "x": X,
    "y": Y,
    "z": Z,
    "h": H,
    "s": S,
    "sdg": Sd,
    "t": T,
    "tdg": Td,
    "rx": Rx,
    "ry": Ry,
    "rz": Rz,
    "r": R,
    "cy": Cy,
    "cz": Cz,
    "ch": Ch,
    "swap": Swap,
    "ccx": Ccnot,
    "crx": Crx,
    "cry": Cry,
    "crz": Crz,
    "cu1": Cu1,
    "cu3": Cu3,
    "cswap": Cswap,
    "rxx": Xx,
    "ryy": Yy,
    "rzz": Zz,
}


def qasm_to_gate(gate_name, extended_header=False):

    if gate_name in qasm_gate_table:
        return qasm_gate_table[gate_name]
    else:
        raise ValueError("Gate is not defined: {:}".format(gate_name))
