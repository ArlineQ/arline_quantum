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
    basic_clifford_t,
    basic_google,
    basic_ibm,
    basic_rigetti,
)
from arline_quantum.hardware.basic_hardware import BasicHardware
from arline_quantum.hardware.hardware import Hardware
from arline_quantum.qubit_connectivity.qubit_connectivity import All2All, QubitConnectivity


def hardware_classes_from_module(module):
    """
    :param module: python module to inspect
    :return: key -- class name, value -- hardware class
    :rtype: dict
    """
    return {n: c for n, c in inspect.getmembers(module, inspect.isclass) if issubclass(c, Hardware)}

# Create Hardware by class name
hardware_classes = {}
hardware_classes.update(hardware_classes_from_module(basic_clifford_t))
hardware_classes.update(hardware_classes_from_module(basic_google))
hardware_classes.update(hardware_classes_from_module(basic_ibm))
hardware_classes.update(hardware_classes_from_module(basic_rigetti))


def hardware_by_name(configuration):
    hardware_cfg = configuration["hardware"]

    if "name" in hardware_cfg:
        kwargs = {}
        try:
            kwargs = hardware_cfg["args"]
        except KeyError:
            pass

        return hardware_classes[hardware_cfg["name"]](**kwargs)
    else:
        # Create BasicHardware
        gate_set = GateSet.from_gate_names(hardware_cfg["gate_set"])
        num_qubits = hardware_cfg["num_qubits"]
        name = "{}_{}q".format(gate_set.name, num_qubits)
        connectivity = QubitConnectivity.from_config(hardware_cfg)

        num_gates = None
        if "num_gates" in hardware_cfg:
            num_gates = hardware_cfg["num_gates"]
        return BasicHardware(name, num_qubits, gate_set, connectivity, num_gates)
