import platform
import pytest
from pathlib import Path
from subprocess import CalledProcessError
import auditwheel_patchelf


HERE = Path(__file__).resolve().parent


@pytest.fixture()
def libfoo(tmp_path):
    name = 'libfoo.so.1'
    src = HERE / 'elf_binaries' / name
    path = tmp_path / name
    path.write_bytes(src.read_bytes())
    yield path


@pytest.fixture()
def foo(tmp_path):
    name = 'foo'
    src = HERE / 'elf_binaries' / name
    path = tmp_path / name
    path.write_bytes(src.read_bytes())
    yield path


def test_get_soname_valid(libfoo):
    assert auditwheel_patchelf.get_soname(libfoo) == 'libfoo.so.1'


def test_get_soname_invalid(foo):
    # TODO, shall this throw ?
    assert auditwheel_patchelf.get_soname(foo) == ''


def test_set_soname(libfoo):
    auditwheel_patchelf.set_soname(libfoo, 'libfoo.so.2')
    assert auditwheel_patchelf.get_soname(libfoo) == 'libfoo.so.2'


def test_get_needed(libfoo):
    assert auditwheel_patchelf.get_needed(libfoo) == ['libm.so.6', 'libc.so.6']


def test_replace_needed(libfoo):
    auditwheel_patchelf.replace_needed(libfoo, 'libm.so.6', 'libm.so.7')
    assert auditwheel_patchelf.get_needed(libfoo) == ['libm.so.7', 'libc.so.6']


def test_remove_needed(libfoo):
    auditwheel_patchelf.remove_needed(libfoo, 'libm.so.6')
    assert auditwheel_patchelf.get_needed(libfoo) == ['libc.so.6']
    auditwheel_patchelf.remove_needed(libfoo, 'libc.so.6')
    assert auditwheel_patchelf.get_needed(libfoo) == []


def test_add_needed(libfoo):
    auditwheel_patchelf.add_needed(libfoo, 'libz.so.6')
    assert auditwheel_patchelf.get_needed(libfoo) == ['libz.so.6', 'libm.so.6', 'libc.so.6']


def test_get_rpath(libfoo):
    assert auditwheel_patchelf.get_rpath(libfoo) == ['/opt/foo/lib', '$ORIGIN']


def test_set_rpath(libfoo):
    auditwheel_patchelf.set_rpath(libfoo, ['/lib'])
    assert auditwheel_patchelf.get_rpath(libfoo) == ['/lib']


def test_force_rpath(libfoo):
    # this actually what's done in auditwheel
    auditwheel_patchelf.set_rpath(libfoo, None)
    auditwheel_patchelf.set_rpath(libfoo, ['/lib'], force_rpath=True)
    assert auditwheel_patchelf.get_rpath(libfoo) == ['/lib']


def test_remove_rpath(libfoo):
    auditwheel_patchelf.set_rpath(libfoo, None)
    assert auditwheel_patchelf.get_rpath(libfoo) == []


def test_get_interpreter_invalid(libfoo):
    # TODO, implement a custom exception
    with pytest.raises(CalledProcessError):
        auditwheel_patchelf.get_interpreter(libfoo)


def test_get_interpreter_valid(foo):
    assert '/ld' in auditwheel_patchelf.get_interpreter(foo)


def test_set_interpreter(foo):
    auditwheel_patchelf.set_interpreter(foo, '/lib/ld-foo.so.1')
    assert auditwheel_patchelf.get_interpreter(foo) == '/lib/ld-foo.so.1'
