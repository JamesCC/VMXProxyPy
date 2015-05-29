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

    MAX_AUX_CHANNELS = 16

    RegExMatchComments = re.compile(r"\#.*$")
    RegExMatchRawRights = re.compile(r"\s*([\-\+])?(UNRESTRICTED|INPUTADJ|MAIN|AUX\*|AUX\d+)")

    def __init__(self):
        self.access_codes = {}

    def get_access_rights(self, passcode):
        return self.access_codes.get(passcode, "")

    def _parse_rights(self, passcode, raw_rights_string):
        accessrights = list( "-" * (2+self.MAX_AUX_CHANNELS) )
        success = True
        for (sign, value) in re.findall(self.RegExMatchRawRights, raw_rights_string):
            value = value.upper()
            if sign == "":
                sign = "+"
            elif sign == "-":
                sign = ""
                
            if value == "UNRESTRICTED" and sign == "+":
                accessrights = list( "*M1234567890123456" )
                
            elif value == "INPUTADJ":
                if sign:
                    accessrights[0] = "*"
                else:
                    accessrights[0] = "-"
                
            elif value == "MAIN":
                if sign:
                    accessrights[1] = "M"
                else:
                    accessrights[1] = "-"

            elif value == "AUX*":
                for aux in range(1,self.MAX_AUX_CHANNELS+1):
                    if sign:
                        accessrights[aux+1] = str(aux%10)
                    else:
                        accessrights[aux+1] = "-"
                
            elif value[0:3] == "AUX":
                aux = int( value[3:] )
                if aux > self.MAX_AUX_CHANNELS:
                    success = False
                elif sign:
                    accessrights[aux+1] = value[-1]
                else:
                    accessrights[aux+1] = "-"
        
        if re.sub(self.RegExMatchRawRights, "", raw_rights_string ).strip() != "":
            success = False
        
        if success:
            self.access_codes[ passcode ] = "".join(accessrights)
        
        return success

    def parse_line(self, line):
        line = self.RegExMatchComments.sub("", line).strip()
        if line != "":
            match = re.match( r"(\d+):(.*)$", line )
            if match:
                return self._parse_rights( match.group(1), match.group(2) )
            else:
                return False
                
        # report success
        return True

    def read_file(self, filename):
        line_number = 0
        with open(filename) as file_hdl:
            for line in file_hdl:
                line_number += 1
                if not self.parse_line(line):
                    logging.warning(filename + ":%d bad format: %s", line_number, line.strip())
            logging.info("Access Code Parsing Complete - %d valid access codes", len(self.access_codes))

