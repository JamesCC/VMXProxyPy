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

import threading
import logging

from VMXParser import VMXParser
from VMXStateMonitor import VMXStateMonitor

class VMXSimulator:
    def process(self, string = None):
        return None

class VMXProcessor:
    __lock = threading.Lock()
    
    __stage2Parser = VMXParser()
    __stateMonitor = VMXStateMonitor()
    __OutputParser = VMXParser()
    
    __mixerIO      = VMXSimulator()
    
    def setMixerIO(self, mixerIOObject):
        self.__mixerIO = mixerIOObject

    def process(self, command = ""):
        
        self.__lock.acquire()
    
        # parse stage1 output to split up any concatenated commands
        outputStage2 = self.__stage2Parser.process(command)

        # while any commands to process...
        outputString = ""
        while outputStage2:
            logging.debug(">> " + outputStage2)

            # Send to mixer or simulator dummy function (which will return None)            
            mixerReply = self.__mixerIO.process(outputStage2)
            
            stateMonitorOutput = self.__stateMonitor.process(outputStage2, mixerReply)
            logging.debug("<< " + stateMonitorOutput)

            #outputString += stateMonitorOutput
            outputString += self.__OutputParser.process(stateMonitorOutput)
            
            # check for any further commands (will be the case if a concatenated command)
            outputStage2 = self.__stage2Parser.process()

        if not self.__stage2Parser.isEmpty():
            # This is bomb proofing, this method should not have been called with fragmented
            # commands, so this should never occur.
            logging.warning("Parser should be empty - discarding fragment")
            __stage2Parser.reset()
            
        self.__lock.release()
    
        return( outputString )

