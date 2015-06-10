#!/bin/bash

cd $(dirname $BASH_SOURCE)
python2 VMXProxy "$@"

echo
read -rsp $'Press any key to continue...\n' -n1 key
