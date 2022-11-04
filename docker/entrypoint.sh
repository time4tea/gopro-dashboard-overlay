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
}

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
        addgroup -g "$gid" dash
        adduser -D -u "$uid" -G dash dash
        chown dash:dash /home/dash

        umask 0002
        exec sudo -u "#$uid" -H -E env PATH="$PATH" /venv/bin/$program "$@"
      else
        /venv/bin/$program "$@"
      fi
    fi
fi

