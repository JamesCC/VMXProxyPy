#!/usr/bin/env perl

die "Please supply OPTIONS" unless scalar(@ARGV);

while(<DATA>)
{
    s/__INSTALL_DIR__/$ENV{'PWD'}/;
    s/__ARGS__/@ARGV/;
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
    echo "Supplied options: __ARGS__"
    screen -dmS VMXProxyProxy __INSTALL_DIR__/start_VMXProxy.sh __ARGS__
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

