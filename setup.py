from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy
import os,sys,sysconfig

def distutils_dir_name(dname):
    """Returns the name of a distutils build directory"""
    f = "{dirname}.{platform}-{version[0]}.{version[1]}"
    return f.format(dirname=dname,
                    platform=sysconfig.get_platform(),
                    version=sys.version_info)

builddir = os.path.join('build', distutils_dir_name('lib'))
print builddir

if sys.platform == 'darwin':
    from distutils import sysconfig
    vars = sysconfig.get_config_vars()
    vars['LDSHARED'] = vars['LDSHARED'].replace('-bundle', '-dynamiclib')


rootincdir = os.popen("root-config --incdir").readlines()[0].strip()
rootlibdir = os.popen("root-config --libdir").readlines()[0].strip()
rootlibstr = os.popen("root-config --libs").readlines()[0].strip()
rootlibs = []
for l in rootlibstr.split():
    if "-l" in l.strip():
        #print l.strip()[len("-l"):] 
        rootlibs.append( l.strip()[len("-l"):] )
print rootincdir
print rootlibdir
print rootlibs

def makedicts():
    os.system("rm pysubevent/subevent/dictsubevent.*")
    os.system("rootcint pysubevent/subevent/dictsubevent.cxx -c -I./pysubevent/subevent Flash.hh SubEvent.hh pysubevent/subevent/LinkDef.h")

    os.system("rm pysubevent/cfdiscriminator/dictcfdiscdata.*")
    os.system("rootcint pysubevent/cfdiscriminator/dictcfdiscdata.cxx -c -I./pysubevent/cfdiscriminator CFDFire.hh pysubevent/cfdiscriminator/LinkDef.h")

makedicts()

ext_subeventdata = Extension( "pysubevent/subevent/libsubeventdata",
                              ["pysubevent/subevent/SubEvent.cc","pysubevent/subevent/Flash.cc", "pysubevent/subevent/dictsubevent.cxx"],
                              library_dirs=[rootlibdir],
                              include_dirs=[rootincdir],
                              libraries=rootlibs,
                              language="c++")
ext_cfdiscdata = Extension( "pysubevent/cfdiscriminator/libcfdiscdata",
                            ["pysubevent/cfdiscriminator/CFDFire.cc","pysubevent/cfdiscriminator/dictcfdiscdata.cxx"],
                            library_dirs=[rootlibdir],
                            include_dirs=[rootincdir],
                            libraries=rootlibs,
                            language="c++")
ext_cfdisc = Extension( "pysubevent/cfdiscriminator/libcfdiscriminator",
                        ["pysubevent/cfdiscriminator/CFDiscConfig.cc", "pysubevent/cfdiscriminator/cfdiscriminator.cc"],
                        library_dirs=[rootlibdir],
                        include_dirs=[rootincdir],
                        libraries=rootlibs,
                        language="c++")

cyext_subevent = Extension("pysubevent/pysubevent/cysubeventdisc",
                           ["pysubevent/pysubevent/subeventdata.pyx",
                            "pysubevent/pysubevent/pysubeventmodconfig.pyx",
                            "pysubevent/pysubevent/cysubeventdisc.pyx",
                            "pysubevent/subevent/scintresponse.cc",
                            "pysubevent/subevent/SubEventModule.cc","pysubevent/subevent/SubEventModConfig.cc"],
                           include_dirs=["pysubevent/subevent",rootincdir,"pysubevent/cfdiscriminator"],
                           library_dirs=[rootlibdir],
                           libraries=rootlibs,
                           language='c++')
cyext_cfdisc_libs = ["cfdiscriminator","cfdiscdata"]+rootlibs

cyext_cfdisc = Extension("pysubevent/pycfdiscriminator/cycfdiscriminator",
                         ["pysubevent/pycfdiscriminator/cycfdiscriminator.pyx"],
                         include_dirs=["pysubevent/cfdiscriminator"],
                         library_dirs=["pysubevent/cfdiscriminator",builddir+"/pysubevent/cfdiscriminator",rootlibdir],
                         libraries=["cfdiscriminator","cfdiscdata"]+rootlibs,
                         language="c++")
cythonExtensions = cythonize([cyext_cfdisc])

setup(
    name='pysubevent',
    #ext_modules=[ext_subeventdata,ext_cfdiscdata]+cythonExtensions,
    ext_modules=[ext_cfdiscdata, ext_cfdisc]+cythonExtensions,
    include_dirs=[numpy.get_include()],
    packages=['pysubevent','pysubevent/pysubevent','pysubevent/pycfdiscriminator','pysubevent/utils'],
)  
