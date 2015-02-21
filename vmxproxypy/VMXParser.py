#! /usr/bin/env python

"""A Validator for V-Mixer Serial Port Protocol."""

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

class VMXParser:
    """Parses an (potential fragmented) input stream constructing whole 
    commands. Commands are output one full command at a time, with the 
    exception of concatenated commands which are reformed into individual 
    commands, but are output as one unit."""

    STX = chr(2)
    ACK = chr(6)
    
    def __init__(self):
        self.__in_buffer = ""

    def reset(self):
        """Resets the VMXParser internal state discarding any data 
        fragments."""
        self.__in_buffer = ""
    
    def is_empty(self):
        """Return True if no partial commands are in the internal buffer."""
        if self.__in_buffer:
            return False
        else:
            return True
    
    def process(self, string = None):
        """Accept commands or partial commands, outputting a command only when
        a full command is seen (otherwise an empty string).  Can be called 
        without a parameter to see if there are any more commands."""
        if string is not None:
            self.__in_buffer += string
        output_command = self._parse()
        return output_command

    def _parse(self):
        """Parse the internal buffer, returning the first valid command seen,
        or an empty string otherwise."""
        string = ''
        stx_found = False

        output_command = ""
        for character in self.__in_buffer:
            if output_command:
                # got command - do not parse anything further
                string += character
                continue
            elif character == self.STX:
                # start of command - drop all leading junk 
                string = character
                skip_semis = False
                stx_found = True
            elif character == self.ACK:
                # acknowledgement - drop all leading junk and assign ACK
                output_command = character
                string = ''
            elif stx_found:
                # start of command seen, wait for semicolon skipping quoted
                if character == '"':
                    # track quotes to know if inside or outside a pair
                    string += character
                    skip_semis = not skip_semis
                elif not skip_semis and character == '&':
                    # concatenated command keep collecting
                    string += ';' + self.STX
                elif not skip_semis and character == ';':
                    # end of command assign to cmd_string
                    string += ';'
                    output_command = string
                    string = ''
                else:
                    string += character
        
        # leave any residue in the buffer for next time
        self.__in_buffer = string
        return output_command 

