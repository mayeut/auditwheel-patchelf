#!/bin/bash -e

python setup.py prepare
./tests/elf_binaries/make_elf_binaries.sh
