#!/bin/bash
env

if [[ -z $REPO_LIST ]]; then

    echo "Env variable REPO_LIST must be specified in the form REPO_LIST=\"cvmfs-config.cern.ch sft.cern.ch\""

else
    for repo in $REPO_LIST; do
        if ! [[ -d /cvmfs/$repo ]]; then
            mkdir /cvmfs/$repo
        fi
        if mountpoint -q /cvmfs/$repo ; then
            umount /cvmfs/$repo
        fi

    mount -t cvmfs $repo /cvmfs/$repo
    done

    while true
    do
        for repo in $REPO_LIST; do
            echo "Checking $repo"
            if mountpoint -q /cvmfs/$repo; then
                echo "$repo OK"
            else
                echo "Remounting $repo ..."
                umount /cvmfs/$repo || exit 1
                mount -t cvmfs $repo /cvmfs/$repo || exit 1
            fi
        done
        sleep 300
    done
fi

