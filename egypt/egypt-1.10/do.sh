#!/bin/bash

set -x
find /mnt/Projects/container-debloating/container-debloating/glibc/build -name "*.expand" > blah
./egypt `cat blah` > out
