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
import logging

class VMXParser:
    """Parses an (potential fragmented) input stream constructing whole commands.
    Commands are output one full command at a time, with the exception of concatenated
    commands which are reformed into individual commands, but are output as one unit."""

    STX = chr(2)
    ACK = chr(6)
    
    __inBuffer = ''         # collector of input text

    def reset(self):
        self.__inBuffer = ""
    
    def isEmpty(self):
        if self.__inBuffer:
            return False
        else:
            return True
    
    def process(self, string = None):
        if string is not None:
            self.__inBuffer += string
        outputCommand = self._parse()
        return outputCommand

    def _parse(self):
        cmdString = ''
        string = ''
        stxFound=False
        complete=False

        outputCommand = ""
        for c in self.__inBuffer:
            if outputCommand:
                # got command - do not parse anything further
                string += c
                continue
            elif c == self.STX:
                # start of command - drop all leading junk 
                string = c
                skipSemis = False
                stxFound = True
            elif c == self.ACK:
                # acknowledgement - drop all leading junk and assign to cmdString
                outputCommand = c
                string = ''
            elif stxFound:
                # start of command seen, wait for semicolon skipping ones inside quotes
                if c == '"':
                    # track quotes to know if inside or outside a pair
                    string += c
                    skipSemis = not skipSemis
                elif not skipSemis and c == '&':
                    # concatenated command keep collecting
                    string += ';' + self.STX
                elif not skipSemis and c == ';':
                    # end of command assign to cmdString
                    string += ';'
                    outputCommand = string
                    string = ''
                else:
                    string += c
        
        # leave any residue in the buffer for next time
        self.__inBuffer = string
        return outputCommand 

