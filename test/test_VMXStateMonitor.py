#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" A Unit test module for VMXStateMonitor.

    This file is part of VMXProxyPy.

    VMXProxyPy is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    VMXProxyPy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Less General Public License
    along with VMXProxyPy.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "James Covey-Crump"
__cpyright__ = "Copyright 2018, James Covey-Crump"
__license__ = "LGPLv3"

import unittest
from VMXProxy.VMXStateMonitor import VMXStateMonitor

class TestVMXStateMonitor(unittest.TestCase):
    """Unittests for VMXStateMonitor"""

    def test_vr(self):
        """Test VRC and VRQ."""
        vmxsm = VMXStateMonitor()
        output = vmxsm.simulate(chr(2)+"VRC:1.010,1.010,1.010;")
        self.assertEqual(output, chr(6))
        output = vmxsm.simulate(chr(2)+"VRQ;")
        self.assertEqual(output, chr(2)+"VRS:1.010,1.010,1.010;")

    def test_pt(self):
        """Test PTC and PTQ."""
        vmxsm = VMXStateMonitor()
        output = vmxsm.simulate(chr(2)+"PTC:I1,1;")
        self.assertEqual(output, chr(6))
        output = vmxsm.simulate(chr(2)+"PTQ:I1;")
        self.assertEqual(output, chr(2)+"PTS:I1,1;")

    def test_pg(self):
        """Test PGC and PGQ."""
        vmxsm = VMXStateMonitor()
        output = vmxsm.simulate(chr(2)+"PGC:I1,0,-65;")
        self.assertEqual(output, chr(6))
        output = vmxsm.simulate(chr(2)+"PGQ:I1;")
        self.assertEqual(output, chr(2)+"PGS:I1,0,-65;")

    def test_ax(self):
        """Test AXC and AXQ commands to simulator directly."""
        vmxsm = VMXStateMonitor()
        output = vmxsm.simulate(chr(2)+"AXC:I2,AX10,-80.0,C;")
        self.assertEqual(output, chr(6))
        output = vmxsm.simulate(chr(2)+"AXQ:I2,AX10;")
        self.assertEqual(output, chr(2)+"AXS:I2,AX10,-80.0,C;")

    def test_ax_mixer(self):
        """Test AXC and AXQ commands via Cache."""
        vmxsm = VMXStateMonitor()
        output = vmxsm.process(chr(2)+"AXQ:I2,AX10;", chr(2)+"AXS:I2,AX10,-80.0,C;")
        self.assertEqual(output, chr(2)+"AXS:I2,AX10,-80.0,C;")
        output = vmxsm.simulate(chr(2)+"AXQ:I2,AX10;")
        self.assertEqual(output, chr(2)+"AXS:I2,AX10,-80.0,C;")

    def test_mx(self):
        """Test MXC and MXQ."""
        vmxsm = VMXStateMonitor()
        output = vmxsm.simulate(chr(2)+"MXC:I2,MX1,-80.0,C;")
        self.assertEqual(output, chr(6))
        output = vmxsm.process(chr(2)+"MXQ:I2,MX1;", chr(2)+"MXS:I2,MX1,-80.0,C;")
        self.assertEqual(output, chr(2)+"MXS:I2,MX1,-80.0,C;")
        modified_input, output = vmxsm.read_cache(chr(2)+"MXq:I2,MX1;")
        self.assertEqual(modified_input, chr(2)+"MXQ:I2,MX1;")
        self.assertEqual(output, chr(2)+"MXS:I2,MX1,-80.0,C;")

    def test_cn(self):
        """Test CNQ."""
        vmxsm = VMXStateMonitor()
        output = vmxsm.process(chr(2)+"CNQ:AX1;", chr(2)+'CNS:AX1,"OUT1  ";')
        self.assertEqual(output, chr(2)+'CNS:AX1,"OUT1  ";')
        output = vmxsm.simulate(chr(2)+"CNQ:AX1;")

    def test_bad_command(self):
        """Test a badly formatted command."""
        vmxsm = VMXStateMonitor()
        output = vmxsm.simulate(chr(2)+"PGQQ:I1;")
        self.assertEqual(output, chr(2)+"ERR:0;")

    def test_unrecognised_command(self):
        """Test unrecognised commands are rejected with ERR:0."""
        vmxsm = VMXStateMonitor()
        output = vmxsm.simulate(chr(2)+"WWC:I1;")
        self.assertEqual(output, chr(2)+"ERR:0;")

    def test_reset(self):
        """Test reset mid command."""
        vmxsm = VMXStateMonitor()
        output = vmxsm.simulate(chr(2)+"MXC:I2,MX1,-80.0,C;")
        self.assertEqual(output, chr(6))
        vmxsm.reset()
        output = vmxsm.simulate(chr(2)+"MXQ:I2,MX1;")
        self.assertEqual(output, chr(2)+"ERR:0;")
