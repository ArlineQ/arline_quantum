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


import inspect

from arline_quantum.gate_sets.gate_set import GateSet
from arline_quantum.hardware import (
    clifford_t,
    google,
    ibm,
    ionq,
    rigetti,
    pyzx,
)
from arline_quantum.hardware.hardware import Hardware
from arline_quantum.qubit_connectivities.qubit_connectivity import All2All, QubitConnectivity


def hardware_classes_from_module(module):
    """
    :param module: python module to inspect
    :return: key -- class name, value -- hardware class
    :rtype: dict
    """
    return {n: c for n, c in inspect.getmembers(module, inspect.isclass) if issubclass(c, Hardware)}


# Create Hardware by class name
hardware_classes = {}
hardware_classes.update(hardware_classes_from_module(clifford_t))
hardware_classes.update(hardware_classes_from_module(google))
hardware_classes.update(hardware_classes_from_module(ibm))
hardware_classes.update(hardware_classes_from_module(ionq))
hardware_classes.update(hardware_classes_from_module(rigetti))
hardware_classes.update(hardware_classes_from_module(pyzx))


def hardware_by_name(hardware):
    if isinstance(hardware, Hardware):
        return hardware
    elif isinstance(hardware, dict):
        if "class" in hardware:
            kwargs = {}
            try:
                kwargs = hardware["args"]
            except KeyError:
                pass

            hw = hardware_classes[hardware["class"]](**kwargs)
            try:
                hw.name = hardware["name"]
            except KeyError:
                pass

            try:
                # patching gate set
                gate_set = GateSet.from_config(hardware)
                hw.gate_set = gate_set
            except:
                pass

            return hw
        else:
            # Create Hardware
            gate_set = GateSet.from_config(hardware)
            try:
                name = hardware["name"]
            except KeyError:
                name = "{}".format(gate_set.name)
            connectivity = QubitConnectivity.from_config(hardware)

            num_gates = None
            if "num_gates" in hardware:
                num_gates = hardware["num_gates"]
            return Hardware(name, gate_set, connectivity, num_gates)
    else:
        raise TypeError("Wrong hardware input type")
