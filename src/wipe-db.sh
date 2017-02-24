#!/bin/bash

find . -type f -name *.bin -exec sh -c 'echo "$0";> "$0"' {} \;
