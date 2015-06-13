#! /usr/bin/env python

#    This file is part of VMXProxyPy.
#
#    VMXProxyPy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    VMXProxyPy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Less General Public License
#    along with VMXProxyPy.  If not, see <http://www.gnu.org/licenses/>.
#

import unittest
from VMXProxy.VMXParser import VMXParser

class TestVMXParser(unittest.TestCase):
    """Unittests for VMXParser"""

    def testInputSequence(self):
        vmxparser = VMXParser()
        command = "blah"+vmxparser.STX+"command;junk"+vmxparser.STX+"next;ff"+vmxparser.ACK+vmxparser.STX+"la"
        self.assertEqual( vmxparser.process(command), vmxparser.STX+"command;" )
        self.assertEqual( vmxparser.process(None), vmxparser.STX+"next;" )
        self.assertEqual( vmxparser.process(""), vmxparser.ACK )
        self.assertEqual( vmxparser.process(), "" )
        self.assertEqual( vmxparser.process(), "" )
        self.assertEqual( vmxparser.process("st;"), vmxparser.STX+"last;" )
        self.assertEqual( vmxparser.process(), "" )

    def testInputChainedCommand(self):
        vmxparser = VMXParser()
        self.assertEqual( vmxparser.process(vmxparser.STX+"cmd1&cmd2&cmd3;"), vmxparser.STX+"cmd1;"+vmxparser.STX+"cmd2;"+vmxparser.STX+"cmd3;" )
        self.assertEqual( vmxparser.process(), "" )

    def testQuotes(self):
        vmxparser = VMXParser()
        self.assertEqual( vmxparser.process("nonsense"+vmxparser.STX+'cmd1:I1,"thi;ng";'), vmxparser.STX+'cmd1:I1,"thi;ng";' )
        
    def testIsEmpty(self):
        vmxparser = VMXParser()
        self.assertEqual( vmxparser.process(vmxparser.STX+"cmd1:I1,st"), "")
        self.assertFalse( vmxparser.is_empty() )
        self.assertEqual( vmxparser.process("art;"), vmxparser.STX+"cmd1:I1,start;" )
        self.assertTrue( vmxparser.is_empty() )

    def testReset(self):
        vmxparser = VMXParser()
        self.assertEqual( vmxparser.process(vmxparser.STX+"cmd1:I1,st"), "")
        vmxparser.reset()
        self.assertTrue( vmxparser.is_empty() )
        self.assertEqual( vmxparser.process(vmxparser.STX+"cmd2:I2,param;"), vmxparser.STX+"cmd2:I2,param;" )
        self.assertTrue( vmxparser.is_empty() )

