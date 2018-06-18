#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" Monitors traffic to/from the mixer recording its state.

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
__copyright__ = "Copyright 2018, James Covey-Crump"
__license__ = "LGPLv3"

import logging
import time
import re
import sys


class CacheEntry(object):
    """A Cache Entry slot with timeout"""

    def __init__(self, response):
        self.__response = response
        self.__timestamp = time.time()

    def get_response(self, timeout=float("inf")):
        """Return response for this cache entry if within timeout, else None"""
        if time.time() - self.__timestamp < timeout:
            return self.__response
        else:
            return None


class VMXStateMonitor(object):
    """Monitors traffic to/from the mixer recording its state.  In simulator mode,
    it will lookup from its state database and create an appropriate response
    simulating the presence of a mixer"""

    CACHE_TIMEOUT = 15      # seconds

    __STX_CHR = chr(2)
    __ACK_CHR = chr(6)
    __RegExCmdValidate = re.compile(r"^" + __STX_CHR + r"([A-Z][A-Z])([CSQq])(.*);$")

    # For each command, the number of parameters required to fully qualify
    # the attribute (database key).  All commands must be listed here to be
    # understood by for "simulation purposes" and to be put in the cache.
    # Commands no listed here will be passed onto the mixer (bypass cache)
    # or, in the case of the simulator, return ERR:0;
    #
    # IT IS VERY IMPORTANT THAT YOU CONSIDER BOTH THE FORM OF THE QUERY COMMAND
    # AND THE FORM OF THE SET RESPONSE FOR ALL xx COMMANDS LISTED HERE.  The
    # following must be true:
    #    0: xxQ      ->  xxS:lookupPrevious[xxS]
    #    1: xxQ:a    ->  xxS:a,lookupPrevious[xxS:a]
    #    2: xxQ:a,b  ->  xxS:a,b,lookupPrevious[xxS:a,b]
    __commandDict = {
        # global mixer related
        'SC': 0, 'VR': 0,

        # input related
        'CN': 1, 'CP': 1, 'EQ': 1, 'FD': 1, 'FL': 1, 'GT': 1, 'MU': 1, 'PG': 1,
        'PN': 1, 'PS': 1, 'PT': 1, 'PI': 1, 'PO': 1,

        'AX': 2,
        'MX': 2
    }

    def __init__(self):
        self.__cache = {}

        # following are set after .parse()
        self.__key = ''                 # 2 letter command prefix
        self.__action = ''              # command action (Q read, C or S write)
        self.__key2 = ''                # operand (input)
        self.__value = ''               # separator and state

    def reset(self):
        """Reset the State Monitor clearing its state database"""
        self.__action = ''
        self.__cache.clear()

    def __get_command_action(self, command):
        """Return the Command Action - CSQ"""
        if len(command) > 4 and command[0] == self.__STX_CHR:
            return command[3]
        else:
            return None

    def get_cache_size(self):
        """Return the size of the cache"""
        return sys.getsizeof(self.__cache)

    def read_cache(self, command):
        """See if a query can be answered from the Cache.  Returns None if not."""
        cached_response = None
        if self.__get_command_action(command) == 'q':
            command = command[0:4].upper() + command[4:]      # uppercase the q
            entry = self.__cache.get(command)
            if entry:
                cached_response = entry.get_response(self.CACHE_TIMEOUT)
        return (command, cached_response)

    def simulate(self, command):
        """Simulates the response from a Mixer, by use of the Cache."""
        self._parse(command)
        return self._simulate_response(command)

    def process(self, command, reply):
        """Process an incoming command from the mixer"""
        if reply == self.__ACK_CHR:
            pass        # do nothing
        elif self.__get_command_action(reply) == 'S':
            # sniff response for cache (<stx>xxS)
            self.__cache[command] = CacheEntry(reply)
        return reply

    def _parse(self, command):
        """Parse a command to obtain the key and value pair."""
        matches = self.__RegExCmdValidate.match(command)
        self.__action = ''
        if matches:
            self.__key = matches.group(1)
            self.__key2 = ''
            self.__value = ''
            key_field_count = self.__commandDict.get(self.__key)
            if key_field_count is None:
                logging.warning("Ignoring unrecognised Command: %s", command[1:])
            elif matches.group(3) != "" and not matches.group(3).startswith(":"):
                logging.warning("Ignoring invalid command: %s", command[1:])
            else:
                self.__action = matches.group(2)
                inside_quotes = False
                add_to_value = False
                for character in matches.group(3):
                    if add_to_value:
                        self.__value += character
                    elif character == '"':
                        # track quotes to know if inside or outside a pair
                        self.__key2 += character
                        inside_quotes = not inside_quotes
                    elif not inside_quotes and (character == ',' or character == ':'):
                        if key_field_count == 0:
                            self.__value = character
                            add_to_value = True
                        else:
                            self.__key2 += character
                            key_field_count -= 1
                    else:
                        self.__key2 += character

    def _simulate_response(self, command):
        """Return the simulated response of a Mixer, using the cache."""
        simulated_response = None
        if self.__action == 'C':
            query_command = self.__STX_CHR + self.__key + 'Q' + self.__key2 + ';'
            query_response = self.__STX_CHR + self.__key + 'S' + self.__key2 + self.__value + ';'
            self.__cache[query_command] = CacheEntry(query_response)
            simulated_response = self.__ACK_CHR
        elif self.__action == 'Q':
            entry = self.__cache.get(command)
            if entry:
                simulated_response = entry.get_response()
        if simulated_response is None:
            simulated_response = self.__STX_CHR + "ERR:0;"   # indicate a syntax error
        return simulated_response
