# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("voxels.pyx", compiler_directives={'boundscheck': False, 'wraparound': False, 'language_level': 3},)
)
