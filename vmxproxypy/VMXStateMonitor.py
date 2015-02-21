#! /usr/bin/env python

"""Monitors traffic to/from the mixer recording its state.""" 

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
import re

class VMXStateMonitor:
    """Monitors traffic to/from the mixer recording its state.  In simulator mode,
    it will lookup from its state database and create an appropriate response
    simulating the presence of a mixer""" 

    __STX_CHR = chr(2)
    __ACK_CHR = chr(6)
    __RegExCmdValidate = re.compile(r"^"+__STX_CHR+r"(..)([CSQ])(.*);$")

    # for each command, the number of parameters required to fully qualify 
    # the attribute (database key).  All commands must be listed here to be
    # understood by for "simulation purposes"
    __commandDict = {
        # global mixer related
        'RC': 0, 'SC': 0, 'VR': 0,

        # input related
        'CN': 1, 'CP': 1, 'EQ': 1, 'FD': 1, 'FL': 1, 'GT': 1, 'MU': 1, 'PG': 1,
        'PN': 1, 'PS': 1, 'PT': 1, 'PI': 1, 'PO': 1,

        'AX': 2,
        'MX': 2
    }

    def __init__(self):
        self.__command_string = ''       # input command
        self.__database = {}             # attribute storage
        
        # following are set after .parse()
        self.__key = ''                  # key/attribute for database
        self.__value = ''                # value of the attribute (if writing)
        self.__action = ''               # action (Q read, C or S write)

    def reset(self):
        """Reset the State Monitor clearing its state database."""
        self.__action = ''
        self.__database.clear()

    def process(self, command, reply = None):
        """Process a command to extract state information from it.  If called
        with only the command will simulate the response for any query 
        commands, by looking in it's state database."""
        if reply is None:
            # No Mixer, i.e. Simulation Case - just process the original
            self._parse(command)
            reply = self._interpret()  
        elif reply == self.__ACK_CHR:
            # Mixer Case
            # if it is an ACK the original command must have been a Set 
            # command and so the state must be extracted from the original
            # command.
            self._parse(command)
            self._interpret()
        else:
            # Mixer Case
            # Process the reply which will hold information about the state
            # of the mixer.
            self._parse(reply)
            self._interpret()
        return reply

    def _parse(self, command):
        """Parse a command to obtain the key and value pair."""
        matches = self.__RegExCmdValidate.match(command)
        self.__action = ""
        if matches:
            self.__command_string = command
            self.__key = matches.group(1)
            self.__value = ''
            skip_semis = False
            add_to_value = False
            key_field_count = self.__commandDict.get(self.__key)
            if key_field_count is None:
                logging.warning("Ignoring unrecognised Command: "+command)
            elif matches.group(3) != "" and not matches.group(3).startswith(":"):
                logging.warning("Ignoring invalid command: "+command)
            else:
                self.__key += 'S'
                self.__action = matches.group(2)
                for character in matches.group(3):
                    if add_to_value:
                        self.__value += character
                    elif character == '"':
                        # track quotes to know if inside or outside a pair
                        self.__key += character
                        skip_semis = not skip_semis
                    elif not skip_semis and ( character == ',' or character == ':' ):
                        if key_field_count == 0:
                            add_to_value = True
                        else:
                            self.__key += character
                            key_field_count -= 1
                    else:
                        self.__key += character

    def _interpret(self):
        """Interpret a previously parsed command, to either create a response
        from the state database, or store a value in the state database."""
        if self.__action == 'C':
            self.__database[self.__key] = self.__value
            simulated_response = self.__ACK_CHR
        elif self.__action == 'S':
            self.__database[self.__key] = self.__value
            simulated_response = self.__command_string
        elif self.__action == 'Q':
            simulated_response = self.__STX_CHR + self.__key
            if self.__key.find(':') == -1:
                simulated_response += ':'
            else:
                simulated_response += ','
            simulated_response += self.__database.get(self.__key,'?') + ';'
        else:
            # indicate a syntax error
            simulated_response = self.__STX_CHR + "ERR:0;"
        self.__action = ""
        
        return simulated_response

