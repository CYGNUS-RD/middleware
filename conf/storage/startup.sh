#!/bin/bash
env

bash_file=/root/init.sh
if [ -e "$bash_file" ]; then
    echo "excuting init file"
    echo "STARTNG INIT"
    $bash_file &
else 
    echo "${bash_file} does not exist"
fi 

echo "DONE"
