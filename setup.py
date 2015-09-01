from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
    name='pysubevent',
    ext_modules=cythonize(["cysubeventdisc.pyx","pysubevent/cycfdiscriminator.pyx"]),
    include_dirs=[numpy.get_include()],
    packages=['pysubevent'],
)  
