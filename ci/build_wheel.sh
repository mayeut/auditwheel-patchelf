#!/bin/bash -xe

# argmuents: sdist wheelhouse image

SCRIPT=$(cat <<-END
	/opt/python/cp37-cp37m/bin/python -m pip wheel --no-deps -w /tmp/wheelhouse /sdist/*
	auditwheel repair -w /tmp/manylinux_wheelhouse /tmp/wheelhouse/*.whl
	/opt/python/cp37-cp37m/bin/pip install /tmp/manylinux_wheelhouse/*
	/opt/python/cp37-cp37m/bin/patchelf --version
	/opt/python/cp37-cp37m/bin/pip install pytest
	/tests/elf_binaries/make_elf_binaries.sh
	/opt/python/cp37-cp37m/bin/pytest -v /tests
	cp /tmp/manylinux_wheelhouse/* /wheelhouse/
END
)

function build {
	docker run --rm \
		-v $(realpath "${1}"):/sdist/sdist.tar.gz \
		-v $(realpath "${2}"):/wheelhouse \
		-v $(pwd)/tests:/tests \
		"quay.io/pypa/${3}" \
		/bin/bash -xec "${SCRIPT}"
}

PLATFORM=$(uname -m)
if [ "${PLATFORM}" == "x86_64" ]; then
	build "${1}" "${2}" "manylinux1_x86_64"
	build "${1}" "${2}" "manylinux1_i686"
else
	build "${1}" "${2}" "manylinux2014_${PLATFORM}"
fi
