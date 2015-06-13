#! /usr/bin/env python

"""The Command Processor.  Takes a command or commands and issues them one
command one at a time to the mixer, collecting the responses and echoing them
back.  If the .set_mixer_interface method is not called it will operate in
a simulation mode, which will emulate an attached mixer."""

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
import random
import time

from VMXParser import VMXParser
from VMXStateMonitor import VMXStateMonitor

class VMXProcessor(object):
    """The Command Processor.  Accepts one or more commands, processes them
    and returns the responses."""

    def __init__(self):
        self.__lock = threading.Lock()
        self.__stage2_parser = VMXParser()
        self.__state_monitor = VMXStateMonitor()
        self.__output_parser = VMXParser()
        self.__mixer_if = None
        self.__discard_rate = None
        self.__cmd_delay = None

    def reset(self):
        """Reset the command processor, but preserve state database."""
        self.__stage2_parser.reset()
        self.__output_parser.reset()
        # Intentionally don't reset the state monitor - to preserve db
        if self.__mixer_if:
            self.__mixer_if.reset()

    def set_mixer_interface(self, mixer_if_object):
        """Set the interface for the mixer.  Typically passed an object of the
        VMXSerialPort class, which exposes the serial interface."""
        self.__mixer_if = mixer_if_object

    def set_debug_discard_rate(self, discard_rate):
        """Set command discard rate (debug option).  Randomly discards 1 in X."""
        self.__discard_rate = discard_rate

    def set_debug_cmd_delay_in_ms(self, cmd_delay_in_ms):
        """Set command maximum delay in milliseconds (debug option)."""
        self.__cmd_delay = cmd_delay_in_ms / 1000.0

    def process(self, command=""):
        """Accept a command or commands, process them, returning the
        responses.  Will pass mixer commands to the mixer interface setup via
        the .set_mixer_interface() method."""
        self.__lock.acquire()

        #logging.debug("> " + command)

        # parse stage1 output to split up any concatenated commands
        output_stage2 = self.__stage2_parser.process(command)

        # while any commands to process...
        output_string = ""
        while output_stage2:
            logging.debug(">> " + output_stage2)

            # discard rate is a debug feature
            if self.__discard_rate:
                if random.randint(1, self.__discard_rate) == self.__discard_rate:
                    logging.debug("Discarded Command")
                    output_stage2 = ""
                    continue

            # see if there is a cached value for the command (only applies if a query command)
            output_stage2, state_monitor_output = self.__state_monitor.read_cache(output_stage2)
            if state_monitor_output:
                logging.debug("<< " + state_monitor_output + " (CACHED)")
            else:
                # Send to mixer (if one is setup)
                if self.__mixer_if:
                    mixer_reply = self.__mixer_if.process(output_stage2)
                else:
                    mixer_reply = self.__state_monitor.simulate(output_stage2)

                # cmd delay is a debug feature
                if self.__cmd_delay is not None:
                    time.sleep(random.random()*self.__cmd_delay)

                state_monitor_output = self.__state_monitor.process(output_stage2, mixer_reply)
                logging.debug("<< " + state_monitor_output)

            # parse the output to keep form
            output_string += self.__output_parser.process(state_monitor_output)

            # check for any further commands (will be the case if a concatenated command)
            output_stage2 = self.__stage2_parser.process()

        if not self.__stage2_parser.is_empty():
            # This is bomb proofing, this method should not have been called with fragmented
            # commands, so this should never occur.
            logging.warning("Parser should be empty - discarding fragment")
            self.__stage2_parser.reset()

        #logging.debug("< " + output_string)

        self.__lock.release()
        return output_string
