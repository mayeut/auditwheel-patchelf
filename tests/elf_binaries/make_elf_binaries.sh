#!/bin/bash -xe


if [ -f /.dockerenv ]; then
	make -C $(dirname $0) clean all
else
	HERE=$(dirname $(realpath $0))
	docker run --rm -v ${HERE}:/elf_binaries quay.io/pypa/manylinux2014_x86_64 make -C /elf_binaries clean all
fi
