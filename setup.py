from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy

#scintResponseExtension = Extension("pysubevent/libscintresponse",
#                                   sources=["pysubevent/scintresponse.cc"],
#                                   include_dirs=["pysubevent"])
cythonExtensions = cythonize([ Extension("pysubevent/cycfdiscriminator",
                                         ["pysubevent/cycfdiscriminator.pyx","pysubevent/cfdiscriminator.cc"],
                                         language="c++"),
                               Extension("cysubeventdisc",
                                         ["cysubeventdisc.pyx","pysubevent/scintresponse.cc"],
                                         language='c++')] )
print cythonExtensions

setup(
    name='pysubevent',
    #ext_modules=[scintResponseExtension]+cythonExtensions,
    ext_modules=cythonExtensions,
    include_dirs=[numpy.get_include()],
    packages=['pysubevent'],
)  
