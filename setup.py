from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy
import os

rootincdir = os.popen("root-config --incdir").readlines()[0].strip()
rootlibdir = os.popen("root-config --libdir").readlines()[0].strip()
rootlibstr = os.popen("root-config --libs").readlines()[0].strip()
rootlibs = []
for l in rootlibstr:
    if "-l" in l.strip():
        rootlibs.append( l.strip()[len("-l"):] )
print rootincdir
print rootlibdir
print rootlibs

def makedicts():
    os.system("rm pysubevent/subevent/dictsubevent.*")
    os.system("rootcint pysubevent/subevent/dictsubevent.cxx -c -I./pysubevent/subevent Flash.hh SubEvent.hh")

makedicts()

ext_subeventdata = Extension( "pysubevent/subevent/libsubeventdata",
                              ["pysubevent/subevent/SubEvent.cc","pysubevent/subevent/Flash.cc", "pysubevent/subevent/dictsubevent.cxx"],
                              library_dirs=[rootlibdir],
                              include_dirs=[rootincdir],
                              libraries=rootlibs,
                              language="c++")
cythonExtensions = cythonize([ Extension("pysubevent/cycfdiscriminator",
                                         ["pysubevent/cycfdiscriminator.pyx","pysubevent/cfdiscriminator.cc"],
                                         language="c++"),
                               Extension("cysubeventdisc",
                                         ["cysubeventdisc.pyx","pysubevent/scintresponse.cc"],
                                         language='c++')] )

setup(
    name='pysubevent',
    ext_modules=[ext_subeventdata]+cythonExtensions,
    include_dirs=[numpy.get_include()],
    packages=['pysubevent'],
)  
