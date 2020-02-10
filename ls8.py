#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()

if len(sys.argv) < 2:
    print('Please provide a program to run')
else:
    cpu.load(sys.argv[1])
    cpu.run()