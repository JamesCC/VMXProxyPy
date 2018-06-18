#!/bin/bash

cd $(dirname $BASH_SOURCE)
if [ -x "$(command -v python3)" ]; then
    python3 start_VMXProxy.py "$@"
else
    python start_VMXProxy.py "$@"
fi

#echo && read -rsp $'Press any key to continue...\n' -n1 key
