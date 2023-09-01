#!/bin/bash
docker kill $(docker ps -q) 
./compile.sh 
. ./run.sh
