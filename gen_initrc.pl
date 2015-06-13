#!/usr/bin/env perl

$arg = shift;

while(<DATA>)
{
    next if s/^##(.)#// and $1!=$arg;
    s/__INSTALL_DIR__/$ENV{'PWD'}/;
    print;
}

__DATA__
#! /bin/sh
# /etc/init.d/VMXProxyStartup 

### BEGIN INIT INFO
# Provides:          VMXProxy
# Required-Start:    $remote_fs $syslog
# Should-Start:      avahi
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Simple script to start VMXProxy at boot
# Description:       A simple script that will start / stop VMXPorxy at boot / shutdown.
### END INIT INFO

# If you want a command to always run, put it here


# Carry out specific functions when asked to by the system
case "$1" in
  start)
    echo "Starting VMXProxy"
##0#    echo "Proxy on Port 10000 to /dev/ttyUSB0"
##0#    screen -dmS VMXProxyProxy __INSTALL_DIR__/start_VMXProxy.sh --serial /dev/ttyUSB0 --net 10000
##1#    echo "Simulations on Port 10000 and /dev/ttyUSB0"
##1#    screen -dmS VMXProxyNetSim __INSTALL_DIR__/start_VMXProxy.sh --net 10000
##1#    screen -dmS VMXProxySerialSim __INSTALL_DIR__/start_VMXProxy.sh --serial /dev/ttyUSB0
    ;;

  stop)
    echo "Stopping VMXProxy"
    for session in $(screen -ls VMXProxy | grep -o '[0-9]\{4\}');
    do 
        screen -S ${session} -X quit
    done
    ;;

  restart)
    $0 stop
    $0 start
    ;;

  status)
    screen -ls VMXProxy
    echo "Connect using... sudo screen -r <number>"
    echo "(CTRL-A CTRL-D will detach)"
    ;;

  *)
    echo "Usage: /etc/init.d/VMXProxyStartup {start|stop|restart|status}"
    exit 1
    ;;
esac

exit 0

