#! /usr/bin/env python

"""Reads a file and issues commands to the supplied VMX command parser 
(VMXProcessor) object."""

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

class VMXSimFileParser:
    """An object to read and parse a file to issue commands to the supplied
    VMX command parser (VMXProcessor) object.  The parser also handles 
    comments, blank lines, and confirms the responses match those stated in 
    the file.  Can be used as a test."""

    RegExMatchComments = re.compile(r"\#.*$")
    RegExParse4CommandReply = re.compile(r"^(\<stx\>.*?;)[ \t]\s*(.*)$")

    def __init__(self, cmd_processor):
        self.__cmd_processor = cmd_processor
        self.__cmd_count = 0
        self.__successful_cmd_count = 0

    def issue_sim_command(self, command, expected_reply):
        """Issue a command into the command processor and confirm the response
        matches.  <stx> and <ack> are replaced with binary equivalents.
        Updates internal state varables counting commands and any failures."""
        command_out = command.replace("<stx>", chr(2))
        response = self.__cmd_processor.process(command_out)
        response = response.replace(chr(2),"<stx>").replace(chr(6), "<ack>")
        if response != expected_reply:
            logging.warning("Response to " + command + " was " + response + " not " + expected_reply)
        else:
            self.__successful_cmd_count += 1
        self.__cmd_count += 1

    def parse_line(self, line):
        """Parse a single line from a file, replacing wildcard <input> with 
        multiple lines ranging from I1 to I48, and issuing the command to the 
        command processor."""
        line = self.RegExMatchComments.sub("", line).strip()
        if line != "":
            match = self.RegExParse4CommandReply.match(line)
            if match:
                command = match.group(1)
                expected_reply = match.group(2)
                if command.find("<input>") >= 0:
                    for i in range(1, 48):
                        modified_command = command.replace("<input>", "I%d" % i)
                        self.issue_sim_command(modified_command, expected_reply)
                else:
                    self.issue_sim_command(command, expected_reply)
            else: # no match report failure
                self.__cmd_count += 1
                return False
        # report success
        return True
    

    def read_file(self, filename):
        """Read a file, parsing the lines, and issuing commands to the command
        processor."""
        # simulator mode
        line_number = 0
        with open(filename) as file_hdl:
            for line in file_hdl:
                line_number += 1
                if not self.parse_line(line):
                    logging.warning("line %d bad format: %s", line_number, line )

        if self.__successful_cmd_count == self.__cmd_count:
            logging.info("Simulator Setup Complete")
        else:
            logging.info("Simulator Setup Complete [Command Failures]")
        logging.debug("Executed %d of %d simulation commands successfully", 
                      self.__successful_cmd_count, self.__cmd_count)
        return self.__successful_cmd_count, self.__cmd_count

