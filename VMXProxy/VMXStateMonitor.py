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
import time
import re

class VMXStateMonitor(object):
    """Monitors traffic to/from the mixer recording its state.  In simulator mode,
    it will lookup from its state database and create an appropriate response
    simulating the presence of a mixer"""

    CACHE_TIMEOUT = 15      # seconds

    __STX_CHR = chr(2)
    __ACK_CHR = chr(6)
    __RegExCmdValidate = re.compile(r"^"+__STX_CHR+r"([A-Z][A-Z])([CSQ])(.*);$")

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
        self.__database_timestamps = {}  # attribute timestamp storage

        # following are set after .parse()
        self.__key = ''                  # key/attribute for database
        self.__value = ''                # value of the attribute (if writing)
        self.__action = ''               # action (Q read, C or S write)

    def reset(self):
        """Reset the State Monitor clearing its state database"""
        self.__action = ''
        self.__database.clear()
        self.__database_timestamps.clear()

    def read_cache(self, command):
        """See if a query can be answered from the Cache.  Returns None if not."""
        self._parse(command)
        # interpretQuery will ignore non Query commands
        return self._interpret_query(time_limit=self.CACHE_TIMEOUT)

    def process(self, command, reply=None):
        """Process an incoming command from the mixer"""
        if reply is None:
            # Simulation Case
            self._parse(command)
            reply = self._interpret()
        elif reply == self.__ACK_CHR:
            # Mixer Case: reply is ACK, use initial command to gather info.
            self._parse(command)
            self._interpret()       # preserve reply
        else:
            # Mixer Case: reply is not an ACK
            self._parse(reply)
            self._interpret()       # preserve reply

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
                    elif not skip_semis and (character == ',' or character == ':'):
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
        simulated_response = self._interpret_query(time_limit=None)
        if simulated_response is None:
            simulated_response = self._interpret_command_set()
        if simulated_response is None:
            # indicate a syntax error
            simulated_response = self.__STX_CHR + "ERR:0;"
        return simulated_response

    def _interpret_command_set(self):
        """Interpret a previously parsed command, to create a response
        from the state database, and store a value in the state database."""
        simulated_response = None
        if self.__action == 'C':
            self.__database[self.__key] = self.__value
            self.__database_timestamps[self.__key] = time.time()
            simulated_response = self.__ACK_CHR
        elif self.__action == 'S':
            self.__database[self.__key] = self.__value
            self.__database_timestamps[self.__key] = time.time()
            simulated_response = self.__command_string

        return simulated_response

    def _interpret_query(self, time_limit=None):
        """Interpret a previously parsed command, to create a response
        from the state database."""
        simulated_response = None
        if self.__action == 'Q':
            lookup = self.__database.get(self.__key)
            cache_valid = True
            if time_limit:
                now = time.time()
                timestamp = self.__database_timestamps.get(self.__key, now)
                cache_valid = (now < (timestamp + time_limit))

            if lookup and cache_valid:
                simulated_response = self.__STX_CHR + self.__key
                if self.__key.find(':') == -1:
                    simulated_response += ':'
                else:
                    simulated_response += ','
                simulated_response += lookup + ';'

        return simulated_response
