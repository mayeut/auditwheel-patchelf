import os
from subprocess import check_output, check_call
import sys

from auditwheel_patchelf._version import __version__


PATCHELF = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'patchelf')


def get_soname(path):
    return check_output([PATCHELF, '--print-soname', str(path)]).decode('ascii').strip()


def set_soname(path, soname):
    check_call([PATCHELF, '--set-soname', soname, str(path)])


def get_needed(path):
    needed = check_output([PATCHELF, '--print-needed', str(path)]).decode('ascii').strip().split('\n')
    if len(needed) == 1 and needed[0] == '':
        return []
    return needed


def replace_needed(path, library, new_library):
    check_call([PATCHELF, '--replace-needed', library, new_library, str(path)])


def remove_needed(path, library):
    check_call([PATCHELF, '--remove-needed', library, str(path)])


def add_needed(path, library):
    check_call([PATCHELF, '--add-needed', library, str(path)])


def get_rpath(path):
    rpaths = check_output([PATCHELF, '--print-rpath', str(path)]).decode('ascii').strip().split(':')
    if len(rpaths) == 1 and rpaths[0] == '':
        return []
    return rpaths


def set_rpath(path, rpath, force_rpath=False):
    if rpath is None:
        args = [PATCHELF, '--remove-rpath', str(path)]
    else:
        args = [PATCHELF, '--set-rpath', ':'.join(rpath), str(path)]
        if force_rpath:
            args.insert(1, '--force-rpath')
    check_call(args)


def get_interpreter(path):
    return check_output([PATCHELF, '--print-interpreter', str(path)]).decode('ascii').strip()


def set_interpreter(path, interpreter):
    check_call([PATCHELF, '--set-interpreter', interpreter, str(path)])


def _main():
    os.execv(PATCHELF, sys.argv)


if __name__ == "__main__":
    _main()
