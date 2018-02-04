import sys
import glob
import serial
import VMXProxy
import logging

#from Tkinter import *
if (sys.version_info > (3, 0)):
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import ttk
else:
    import Tkinter as tk
    import tkFileDialog as filedialog
    import ttk

class simpleapp_tk(tk.Tk):
    MODE_SSIM = 1
    MODE_NSIM = 2
    MODE_SEC_NSIM = 3
    MODE_PROXY = 4
    MODE_SEC_PROXY = 5


    def __init__(self,parent):
        tk.Tk.__init__(self,parent)
        self.parent = parent
        self.options = None
        
        self.net_port = tk.IntVar()
        self.serial_port = tk.StringVar()
        self.baud_rate = tk.IntVar()
        self.passcode_file = tk.StringVar()
        self.mode = tk.IntVar()
        self.passcode_enable = tk.BooleanVar()
        self.verbosity = tk.IntVar()

        self.find_serial_ports()
        self.initialize()
        self.set_variables()
        self.widget_enables_callback()
        self.layout()

    
    def initialize(self):
        self.row=1
        self.mainframe = ttk.Frame(self.parent, padding="10 10 10 10")
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)

        self.mode_label = ttk.Label(self.mainframe, text="Mode:")
        self.r1 = ttk.Radiobutton(self.mainframe, text="Simulator on Serial Port", variable=self.mode, value=self.MODE_SSIM, command=self.widget_enables_callback)
        self.r2 = ttk.Radiobutton(self.mainframe, text="Simulator on Network", variable=self.mode, value=self.MODE_NSIM, command=self.widget_enables_callback)
        self.r3 = ttk.Radiobutton(self.mainframe, text="Secure Simulator on Network", variable=self.mode, value=self.MODE_SEC_NSIM, command=self.widget_enables_callback)
        self.r4 = ttk.Radiobutton(self.mainframe, text="Network to Serial Proxy", variable=self.mode, value=self.MODE_PROXY, command=self.widget_enables_callback)
        self.r5 = ttk.Radiobutton(self.mainframe, text="Secure Network to Serial Proxy", variable=self.mode, value=self.MODE_SEC_PROXY, command=self.widget_enables_callback)

        self.empty_label = ttk.Label(self.mainframe, text="")

        self.networkport_label = ttk.Label(self.mainframe, text="Network port:")
        self.net_port_widget = ttk.Entry(self.mainframe, width=7, textvariable=self.net_port)

        self.serialport_label = ttk.Label(self.mainframe, text="Serial port:")
        self.serial_port_widget = tk.OptionMenu(self.mainframe, self.serial_port, *self.serial_ports_list)

        self.baudrate_label = ttk.Label(self.mainframe, text="Baud Rate:")
        self.baud_rate_widget = ttk.Entry(self.mainframe, width=7, textvariable=self.baud_rate)

        self.passcode_file_label = ttk.Label(self.mainframe, text="Passcode File:")
        self.passcode_file_widget = ttk.Entry(self.mainframe, width=32, textvariable=self.passcode_file)
        self.passcode_file_button = ttk.Button(self.mainframe, text='...', width=3, command=self.askopenfilename)
        
        self.verbose_checkbutton = ttk.Checkbutton(self.mainframe, text="Verbose", variable=self.verbosity)

        self.start_server_button = ttk.Button(self.mainframe, text="Start Server", command=self.start_server)
        self.exit_button = ttk.Button(self.mainframe, text="Exit", command=self.destroy)

    def layout_in_row(self, a, b=None, c=None, padding=3):
        if a is not None:
            a.grid(row=self.row, sticky=tk.E, padx=padding, pady=padding)
        if b is not None:
            b.grid(row=self.row, column=1, sticky=tk.W, padx=padding, pady=padding)
        if c is not None:
            c.grid(row=self.row, column=2, sticky=tk.W, padx=padding, pady=padding)
        self.row += 1

    def layout(self):
        self.layout_in_row(self.mode_label, self.r1, padding=0)
        self.layout_in_row(None, self.r2, padding=0)
        self.layout_in_row(None, self.r3, padding=0)
        self.layout_in_row(None, self.r4, padding=0)
        self.layout_in_row(None, self.r5, padding=0)
        self.layout_in_row(self.empty_label, padding=0)
        self.layout_in_row(self.networkport_label, self.net_port_widget)
        self.layout_in_row(self.serialport_label, self.serial_port_widget)
        self.layout_in_row(self.baudrate_label, self.baud_rate_widget)
        self.layout_in_row(self.passcode_file_label, self.passcode_file_widget, self.passcode_file_button)
        self.layout_in_row(None, self.verbose_checkbutton)
        self.layout_in_row(self.start_server_button, self.exit_button, None)

    def set_variables(self):
        self.net_port.set(10000)
        self.serial_port.set(self.serial_ports_list[0])
        self.baud_rate.set(115200)
        self.passcode_file.set("passcodes.txt")
        self.mode.set(2)
        self.passcode_enable.set(False)

    def askopenfilename(self):
        """Returns an opened file in read mode.
        This time the dialog just returns a filename and the file is opened by your own code.
        """

        # define options for opening or saving a file
        file_opt = options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        options['initialfile'] = 'passcodes.txt'
        options['parent'] = tk.root
        options['title'] = 'Choose passcodes file'

        # get filename
        filename = filedialog.askopenfilename(**file_opt)
        if filename:
            self.passcode_file.set(filename)

    def widget_enables_callback(self):
        if self.mode.get() == self.MODE_SSIM:
            self.net_port_widget.configure(state=tk.DISABLED)
            self.serial_port_widget.configure(state=tk.NORMAL)
            self.baud_rate_widget.configure(state=tk.NORMAL)
            self.passcode_file_widget.configure(state=tk.DISABLED)
            self.passcode_file_button.configure(state=tk.DISABLED)
        elif self.mode.get() == self.MODE_NSIM:
            self.net_port_widget.configure(state=tk.NORMAL)
            self.serial_port_widget.configure(state=tk.DISABLED)
            self.baud_rate_widget.configure(state=tk.DISABLED)
            self.passcode_file_widget.configure(state=tk.DISABLED)
            self.passcode_file_button.configure(state=tk.DISABLED)
        elif self.mode.get() == self.MODE_SEC_NSIM:
            self.net_port_widget.configure(state=tk.NORMAL)
            self.serial_port_widget.configure(state=tk.DISABLED)
            self.baud_rate_widget.configure(state=tk.DISABLED)
            self.passcode_file_widget.configure(state=tk.NORMAL)
            self.passcode_file_button.configure(state=tk.NORMAL)
        elif self.mode.get() == self.MODE_PROXY:
            self.net_port_widget.configure(state=tk.NORMAL)
            self.serial_port_widget.configure(state=tk.NORMAL)
            self.baud_rate_widget.configure(state=tk.NORMAL)
            self.passcode_file_widget.configure(state=tk.DISABLED)
            self.passcode_file_button.configure(state=tk.DISABLED)
        elif self.mode.get() == self.MODE_SEC_PROXY:
            self.net_port_widget.configure(state=tk.NORMAL)
            self.serial_port_widget.configure(state=tk.NORMAL)
            self.baud_rate_widget.configure(state=tk.NORMAL)
            self.passcode_file_widget.configure(state=tk.NORMAL)
            self.passcode_file_button.configure(state=tk.NORMAL)
        else:
            self.passcode_file_widget.configure(state=tk.DISABLED)
            self.net_port_widget.configure(state=tk.DISABLED)
            self.serial_port_widget.configure(state=tk.DISABLED)
            self.baud_rate_widget.configure(state=tk.DISABLED)
            self.passcode_file_widget.configure(state=tk.DISABLED)
            self.passcode_file_button.configure(state=tk.DISABLED)

        if not self.serial_ports_found:
            self.r1.configure(state=tk.DISABLED)
            self.r4.configure(state=tk.DISABLED)
            self.r5.configure(state=tk.DISABLED)
            self.serial_port_widget.configure(state=tk.DISABLED)
            self.baud_rate_widget.configure(state=tk.DISABLED)
        else:
            self.r1.configure(state=tk.NORMAL)
            self.r4.configure(state=tk.NORMAL)
            self.r5.configure(state=tk.NORMAL)

        self.start_server_button.configure(state=tk.NORMAL)

    def start_server(self):
        self.options = {"serial" : None, "baudrate" : None, 
                        "port" : None, "passcodefile" : None,
                        "verbosity" : False}
        
        if self.verbosity.get() == 1:
            self.options["verbosity"] = True
        
        if self.mode.get() == self.MODE_SSIM:
            self.options["serial"] = self.serial_port.get()
            self.options["baudrate"] = self.baud_rate.get()
        elif self.mode.get() == self.MODE_NSIM:
            self.options["port"] = self.net_port.get()
        elif self.mode.get() == self.MODE_SEC_NSIM:
            self.options["port"] = self.net_port.get()
            self.options["passcodefile"] = self.passcode_file.get()
        elif self.mode.get() == self.MODE_PROXY:
            self.options["serial"] = self.serial_port.get()
            self.options["baudrate"] = self.baud_rate.get()
            self.options["port"] = self.net_port.get()
        elif self.mode.get() == self.MODE_SEC_PROXY:
            self.options["serial"] = self.serial_port.get()
            self.options["baudrate"] = self.baud_rate.get()
            self.options["port"] = self.net_port.get()
            self.options["passcodefile"] = self.passcode_file.get()

        self.destroy()
        
    def get_options(self):
        return(self.options)

    def find_serial_ports(self):
        """Lists serial ports

        :raises EnvironmentError:

            On unsupported or unknown platforms
        :returns:
            A list of available serial ports
        """
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[US]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        self.serial_ports_list = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                self.serial_ports_list.append(port)
            except (OSError, serial.SerialException):
                pass

        if len(self.serial_ports_list) == 0:
            self.serial_ports_list.append("none found")
            self.serial_ports_found = False
        else:
            self.serial_ports_found = True

def start_gui(options):
    app = simpleapp_tk(None)
    app.title("VMXProxyGUI")
    app.resizable(width=False,height=False);
    app.mainloop()
    
    if app.options is None:
        options = None
        return
    
    options.serial = app.options["serial"]
    options.baud = app.options["baudrate"]
    options.port = app.options["port"]
    options.passcodefile = app.options["passcodefile"]
    options.verbosity = app.options["verbosity"]
