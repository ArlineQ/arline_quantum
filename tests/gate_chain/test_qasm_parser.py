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


import unittest
from os import path
import numpy as np

from arline_quantum.gate_chain.gate_chain import GateChain


class TestQasmParser(unittest.TestCase):
    def test_2q_qasm_parser(self):
        basepath = path.dirname(__file__)
        input_dir = path.abspath(path.join(basepath, "..", "qasm_files", "general", "2q.qasm"))
        test_dir = path.dirname(path.abspath(__file__))
        output_dir = path.join(test_dir, "2q_result.qasm")
        gate_chain = GateChain.from_qasm(input_dir)
        gate_chain.save_to_qasm(output_dir, qreg_name="q")

        file = open(input_dir, mode="r", encoding="utf-8-sig")
        lines_ref = file.readlines()
        file.close()
        file = open(output_dir, mode="r", encoding="utf-8-sig")
        lines_res = file.readlines()
        file.close()
        np.testing.assert_equal(lines_res, lines_ref)

    def test_small_angle_qasm_parser(self):
        basepath = path.dirname(__file__)
        input_dir = path.abspath(path.join(basepath, "..", "qasm_files", "general", "small_angle.qasm"))
        test_dir = path.dirname(path.abspath(__file__))
        output_dir = path.join(test_dir, "small_angle_result.qasm")
        gate_chain = GateChain.from_qasm(input_dir)
        gate_chain.save_to_qasm(output_dir, qreg_name="q0", creg_name="c0")

        file = open(input_dir, mode="r", encoding="utf-8-sig")
        lines_ref = file.readlines()
        file.close()
        file = open(output_dir, mode="r", encoding="utf-8-sig")
        lines_res = file.readlines()
        file.close()
        np.testing.assert_equal(lines_res, lines_ref)


if __name__ == "__main__":
    unittest.main()
