#! /usr/bin/env python

"""Reads an passcode file and creates a dictionary of access rights indexed
by passcode."""

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

class VMXPasscodeParser(object):
    """Parses an passcode file for passcodes and their access rights, for
    later retrieval"""
    MAX_AUX_CHANNELS = 16
    UNRESTRICTED_RIGHTS = "*M1234567890123456"

    RegExMatchComments = re.compile(r"\#.*$")
    RegExMatchRawRights = re.compile(r"\s*([\-\+])?(UNRESTRICTED|INPUTADJ|MAIN|AUX\*|AUX\d+)")

    def __init__(self):
        self.access_codes = {}

    def get_access_rights(self, passcode):
        """Return access rights for the given passcode, else an empty string
        if not found"""
        return self.access_codes.get(passcode, "")

    def _parse_rights(self, passcode, raw_rights_string):
        """Parse access right to turn into condensed form"""
        accessrights = list("-" * (2+self.MAX_AUX_CHANNELS))
        success = True
        for (sign, value) in re.findall(self.RegExMatchRawRights, raw_rights_string):
            value = value.upper()

            allow = True if (sign == "" or sign == "+") else False

            if value == "UNRESTRICTED" and allow:
                accessrights = list(self.UNRESTRICTED_RIGHTS)

            elif value == "INPUTADJ":
                accessrights[0] = "*" if allow else "-"

            elif value == "MAIN":
                accessrights[1] = "M" if allow else "-"

            elif value == "AUX*":
                for aux in range(1, self.MAX_AUX_CHANNELS+1):
                    accessrights[aux+1] = str(aux%10) if allow else "-"

            elif value[0:3] == "AUX":
                aux = int(value[3:])
                if aux < 1 or aux > self.MAX_AUX_CHANNELS:
                    success = False
                else:
                    accessrights[aux+1] = value[-1] if allow else "-"

        if re.sub(self.RegExMatchRawRights, "", raw_rights_string).strip() != "":
            success = False

        if success:
            self.access_codes[passcode] = "".join(accessrights)

        return success

    def parse_line(self, line):
        """Parse a line for passcodes and access rights"""
        line = self.RegExMatchComments.sub("", line).strip()
        if line != "":
            match = re.match(r"(\d+):(.*)$", line)
            if match:
                return self._parse_rights(match.group(1), match.group(2))
            else:
                return False

        # report success
        return True

    def read_file(self, filename):
        """Open and read an passcode file and parse line by line"""
        line_number = 0
        try:
            with open(filename) as file_hdl:
                for line in file_hdl:
                    line_number += 1
                    if not self.parse_line(line):
                        logging.warning(filename + ":%d bad format: %s", line_number, line.strip())
                logging.info("Access Code Parsing Complete - %d valid access codes", len(self.access_codes))

        except IOError:
            logging.info("Unable to open Access Code file - "+filename+" (server is locked down)")
