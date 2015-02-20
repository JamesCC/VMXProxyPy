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
import re

class VMXSimFileParser:

    RegExMatchComments = re.compile("\#.*$")
    RegExParse4CommandReply = re.compile("^(\<stx\>.*?;)[ \t]\s*(.*)$")

    def __init__(self, cmdProcessor):
        self.__cmdProcessor = cmdProcessor
        self.__commandCount = 0;
        self.__successfulCommandCount = 0;

    def IssueSimCommand(self, command, expectedReply):
        commandOut = command.replace("<stx>",chr(2));
        response = self.__cmdProcessor.process(commandOut);
        response = response.replace(chr(2),"<stx>").replace(chr(6),"<ack>");
        if response != expectedReply:
            logging.warning("Response to " + command + " was " + response + " not " + expectedReply)
        else:
            self.__successfulCommandCount += 1
        self.__commandCount += 1

    def ParseLine(self, line):
        line = self.RegExMatchComments.sub("", line).strip()
        if line != "":
            match = self.RegExParse4CommandReply.match(line)
            if match:
                command = match.group(1);
                expectedReply = match.group(2)
                if command.find("<input>") >= 0:
                    for i in range(1, 48):
                        modifiedCommand = command.replace("<input>","I%d" % i)
                        self.IssueSimCommand(modifiedCommand, expectedReply)
                else:
                    self.IssueSimCommand(command, expectedReply)
            else: # no match report failure
                self.__commandCount += 1
                return False
        # report success
        return True
    

    def ReadFile(self, filename):
        # simulator mode
        lineNumber = 0
        with open(filename) as f:
            for line in f:
                lineNumber += 1
                if not self.ParseLine(line):
                    logging.warning("line %d bad format: %s" % ( lineNumber, line ))

        if self.__successfulCommandCount == self.__commandCount:
            logging.info("Simulator Setup Complete")
        else:
            logging.info("Simulator Setup Complete [Command Failures]")
        logging.debug("Executed %d of %d simulation commands successfully" 
                      % (self.__successfulCommandCount, self.__commandCount))
        return self.__successfulCommandCount, self.__commandCount

