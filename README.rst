.. SETUP VARIABLES
.. |license-status| image:: https://img.shields.io/badge/license-GPLv3-blue.svg
  :target: https://github.com/mayeut/auditwheel-patchelf/blob/master/LICENSE
.. |pypi-status| image:: https://img.shields.io/pypi/v/auditwheel-patchelf.svg
  :target: https://pypi.python.org/pypi/auditwheel-patchelf
.. |python-versions| image:: https://img.shields.io/pypi/pyversions/auditwheel-patchelf.svg
.. |travis-status| image:: https://travis-ci.com/mayeut/auditwheel-patchelf.svg?branch=master
  :target: https://travis-ci.com/mayeut/auditwheel-patchelf
.. END OF SETUP

auditwheel-patchelf
===================

|license-status| |pypi-status| |python-versions| |travis-status|

This project is a python wrapper on `patchelf <https://github.com/NixOS/patchelf>`_.

Since ``patchelf`` doesn't provide a library API, the executable is used to make all calls.
The executable is provided by the package and will also be available for direct use after installation.

It aims to provide a simple way to provide ``patchelf`` when working with `auditwheel <https://github.com/pypa/auditwheel>`_.

Installation
============

.. code::

    pip install auditwheel-patchelf

Usage
=====
[WIP]
