cimport cython

cdef extern from "CFDiscConfig.hh" namespace "cpysubevent":
    cdef cppclass CFDiscConfig:
        CFDiscConfig() except +
        int delay
        int threshold
        int deadtime
        int width
        int gate

cdef extern from "SubEventModConfig.hh" namespace "subevent":
    cdef cppclass SubEventModConfig:
        SubEventModConfig() except +
        double spe_sigma
        double fastfraction
        double slowfraction
        double fastconst_ns
        double slowconst_ns
        int npresamples
        int pedsamples
        double pedmaxvar
        double nspersample
        CFDiscConfig cfdconfig

