import glob
import os
import runpy
import shutil
import sys

from distutils import log
from distutils.cmd import Command
from setuptools.command.sdist import sdist
from setuptools.command.build_ext import build_ext
from setuptools import find_packages, Extension, setup
from subprocess import check_call, check_output, CalledProcessError, DEVNULL
from wheel.bdist_wheel import bdist_wheel


HERE = os.path.abspath(os.path.dirname(__file__))
VERSION_FILE = os.path.join(HERE, 'src', 'auditwheel_patchelf', '_version.py')


def prepare_version():
    if os.path.exists(os.path.join(HERE, 'patchelf', 'version')):
        with open(os.path.join(HERE, 'patchelf', 'version'), 'rt') as f:
            patchelf_version = [int(p) for p in f.readline().split('.')]
    else:
        patchelf_version = [0]
    while len(patchelf_version) < 3:
        patchelf_version.append(0)
    if os.path.exists('.git'):
        build_min_version = 0 if len(glob.glob(os.path.join(HERE, 'patches', '*.diff'))) == 0 else 1
        git_tag = None
        is_tag = False
        try:
            git_tag = check_output(['git', 'describe', '--tags', '--exact-match', '--dirty'], stderr=DEVNULL).decode('ascii').strip()
            if git_tag.endswith('-dirty'):
                git_tag = git_tag[0:-6]
            else:
                is_tag = True
        except CalledProcessError:
            pass
        if git_tag is None:
            try:
                git_tag = check_output(['git', 'describe', '--tags', '--candidates=1'], stderr=DEVNULL).decode('ascii').strip()
            except CalledProcessError:
                pass
        if git_tag is not None:
            git_tag = [int(p) for p in git_tag[1:].split('.')]
            assert patchelf_version >= git_tag[0:3]
            if patchelf_version > git_tag[0:3]:
                git_tag = None
        if git_tag is None:
            build_version = build_min_version
        else:
            build_version = git_tag[3] if is_tag else git_tag[3] + 1
    elif not os.path.exists(VERSION_FILE):
        build_version = 0
    else:
        return
    patchelf_version.append(build_version)
    with open(VERSION_FILE, 'wt') as f:
        f.write('__version__ = "{}.{}.{}.{}"\n'.format(*patchelf_version))


def prepare_sources():
    src_dir = os.path.join(HERE, 'patchelf')
    dst_dir = os.path.join(HERE, 'src', 'patchelf')
    if not os.path.exists(src_dir):
        # building from sdist
        return
    if os.path.exists(dst_dir):
        log.info('removing folder {}'.format(dst_dir))
        shutil.rmtree(dst_dir)
    log.info('copying folder {} to {}'.format(src_dir, dst_dir))
    shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns('.*'))
    patches = glob.glob(os.path.join(HERE, 'patches', '*.diff'))
    patches.sort()
    log.info('patching files in {}'.format(dst_dir))
    for patch in patches:
        check_call(['patch', '-d', dst_dir, '-p1', '-i', patch])


def prepare_all():
    prepare_sources()
    prepare_version()


def get_version():
    prepare_version()
    return runpy.run_path(VERSION_FILE)['__version__']


def build_patchelf():
    try:
        curdir = os.path.abspath(os.curdir)
        os.chdir(os.path.join(HERE, 'src', 'patchelf'))
        check_call(['./bootstrap.sh'])
        check_call(['./configure'])
        check_call(['make'])
        if sys.platform.startswith('linux'):
            check_call(['make', 'check'])
        path = os.path.abspath('src/patchelf')
        if sys.platform.startswith('linux'):
            check_call(['strip', '--strip-unneeded', path])
    finally:
        os.chdir(curdir)
    return path


class BuildExt(build_ext):
    def run(self):
        fn = build_patchelf()
        shutil.copy(fn, os.path.join(self.output_dir(), 'patchelf'))

    def output_dir(self):
        if not self.inplace:
            return os.path.join(self.get_finalized_command('build').build_platlib, 'auditwheel_patchelf')

        build_py = self.get_finalized_command('build_py')
        package_dir = os.path.abspath(build_py.get_package_dir('auditwheel_patchelf'))
        return package_dir


class BDistWheel(bdist_wheel):
    def get_tag(self):
        impl_tag, abi_tag, plat_tag = super().get_tag()
        return 'py3', 'none', plat_tag


class SDist(sdist):
    def run(self):
        prepare_all()
        super().run()


# Let's define a class to clean in-place built extensions
class PrepareCommand(Command):
    """A custom command to prepare sources."""

    description = 'prepare sources'
    user_options = []

    def initialize_options(self):
        """Set default values for options."""

    def finalize_options(self):
        """Post-process options."""

    def run(self):
        """Run command."""
        prepare_all()


with open(os.path.join(HERE, 'README.rst'), 'rt') as f:
    LONG_DESCRIPTION = f.read()

setup(
    cmdclass={
        'sdist': SDist,
        'build_ext': BuildExt,
        'bdist_wheel': BDistWheel,
        'prepare': PrepareCommand,
    },
    name="auditwheel_patchelf",
    version=get_version(),
    description="patchelf python wrapper for auditwheel.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    license='GPLv3',
    license_file='LICENSE',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Software Development :: Build Tools",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
    url='https://github.com/mayeut/auditwheel-patchelf/',
    keywords='wheel manylinux auditwheel',
    project_urls={
        # "Documentation": "https://github.com/mayeut/auditwheel-patchelf/",
        "Source": "https://github.com/mayeut/auditwheel-patchelf/",
        # "Changelog": "https://github.com/mayeut/auditwheel-patchelf/",
    },

    author='Matthieu Darbois',
    # author_email='mayeut@users.noreply.github.com',

    package_dir={"": "src"},
    packages=find_packages(where="src"),
    ext_modules=[
        Extension('auditwheel_patchelf.mock', ['auditwheel_patchelf.mock'])
    ],
    entry_points={
        "console_scripts": [
            "auditwheel_patchelf=auditwheel_patchelf:_main",
        ],
    },

    zip_safe=False,
    python_requires='>=3.5',
)
