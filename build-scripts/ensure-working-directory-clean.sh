#!/bin/bash

FILES=$(git status --porcelain | egrep -v '^\?\?')

if [ "$FILES" != "" ]
then
  echo "Working Directory not clean"
  echo $FILES
  exit 1
fi

