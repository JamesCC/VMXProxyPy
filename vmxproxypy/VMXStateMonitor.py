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

import logging
import unittest
import re

class VMXStateMonitor:

    __STX_CHR=chr(2)
    __ACK_CHR=chr(6)
    __RegExCmdValidate = re.compile("^"+__STX_CHR+"(..)([CSQ])(.*);$")

    # for each command, the number of parameters required to fully qualify the attribute (database key)
    # all commands must be listed here to be understood by for "simulation purposes"
    __commandDict = {
        # global mixer related
        'RC': 0, 'SC': 0, 'VR': 0,

        # input related
        'CN': 1, 'CP': 1, 'EQ': 1, 'FD': 1, 'FL': 1, 'GT': 1, 'MU': 1, 'PG': 1,
        'PI': 1, 'PN': 1, 'PS': 1, 'PT': 1, 'PI': 1, 'PO': 1,

        'AX': 2,
        'MX': 2
    }

    __commandString = ''        # input command
    __outputString = ''         # output response
    __database = {}             # attribute storage
    
    # following set after .parse()
    __key = ''                  # key/attribute for database
    __value = ''                # value of the attribute for database (if writing)
    __action = ''               # action (Q read, C or S write)

    def reset(self):
        self.__action =''
        self.__database.clear()

    def process(self, command, reply = None):
        if reply is None:
            # No Mixer, i.e. Simulation Case - just process the original command
            self._parse(command)  
        elif reply == self.__ACK_CHR:
            # if it is an ACK the original command must have been a Set command (e.g. PTC) and the 
            # _process() method will return ACK when working on the original command.
            self._parse(command)
        else:
            self._parse(reply)
        self.__outputString = reply
        return self._interpret()

    def _parse(self, command):
        matches = self.__RegExCmdValidate.match(command)
        self.__action = ""
        if matches:
            self.__commandString = command
            self.__key = matches.group(1)
            self.__value = ''
            skipSemis = False
            addToValue = False
            keyFieldCount = self.__commandDict.get(self.__key)
            if keyFieldCount is None:
                logging.warning("Ignoring unrecognised Command: "+command)
            elif matches.group(3) != "" and not matches.group(3).startswith(":"):
                logging.warning("Ignoring invalid command: "+command)
            else:
                self.__key += 'S'
                self.__action = matches.group(2)
                for c in matches.group(3):
                    if addToValue:
                        self.__value += c
                    elif c == '"':
                        # track quotes to know if inside or outside a pair
                        self.__key += c
                        skipSemis = not skipSemis
                    elif not skipSemis and ( c == ',' or c == ':' ):
                        if keyFieldCount == 0:
                            addToValue = True
                        else:
                            self.__key += c
                            keyFieldCount -= 1
                    else:
                        self.__key += c

    def _interpret(self):
        if self.__action == 'C':
            self.__database[self.__key] = self.__value
            outputString = self.__ACK_CHR
        elif self.__action == 'S':
            self.__database[self.__key] = self.__value
            outputString = self.__commandString
        elif self.__action == 'Q':
            outputString = self.__STX_CHR + self.__key
            if self.__key.find(':') == -1:
                outputString += ':'
            else:
                outputString += ','
            outputString += self.__database.get(self.__key,'?') + ';'
        else:
            # indicate a syntax error
            outputString = self.__STX_CHR + "ERR:0;"
        self.__action = ""
        
        if self.__outputString is None:
            # if self.__outputString is not set must be a simulation environment
            return outputString
        else:
            # if self.__outputString is set we must pass on the response from the Mixer
            return self.__outputString

