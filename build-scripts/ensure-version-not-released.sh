#!/bin/bash

VERSION_TO_CHECK=$1

status=$(curl --head -o /dev/null -s -w "%{http_code}\n" https://pypi.org/project/gopro-overlay/${VERSION_TO_CHECK}/)

if [ $status -ne 404 ]
then
  echo "Version $VERSION_TO_CHECK is already on PyPI"
  exit 1
fi

