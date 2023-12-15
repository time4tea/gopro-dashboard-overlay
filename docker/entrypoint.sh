#!/bin/bash

function show_available() {
    echo "The following commands are available:"
    for p in $(ls -1 /venv/bin | grep 'gopro')
    do
      echo -e "\t$p"
    done

    echo
    echo "The current directory is mapped into the docker container, so program inputs and outputs"
    echo "should be below the current directory, and referenced with relative names"
    echo "e.g. docker ... gopro-dashboard.py movies/input.MP4 overlays/output.MP4"
    echo "Note: use --config-dir and --cache-dir to set location of config (e.g. profiles) and cache"
    echo ".. these should either be below current directory, or use additional volume mounts"
}

set -x

program=$1
shift

if [ "$program" == "" ]
then
    show_available
    exit 1
else
    if [ ! -e /venv/bin/$program ]
    then
      echo "$program: Not Found"
      show_available
      exit 1
    else

      uid=$(ls -ldn . | awk '{print $3}')
      gid=$(ls -ldn . | awk '{print $4}')

      if [ $uid -ne 0 ]
      then
        getent group $gid > /dev/null || groupadd -g "$gid" dash

        if [ ! $(getent passwd $uid) ]; then
          useradd --home-dir /home/dash --create-home --no-user-group --uid "$uid" --gid "$gid" dash
          chown $uid:$gid /home/dash
        fi

        umask 0002
        exec sudo -u "#$uid" -H -E env PATH="$PATH" /venv/bin/$program "$@"
      else
        /venv/bin/$program "$@"
      fi
    fi
fi

