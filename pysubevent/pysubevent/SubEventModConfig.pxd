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
        double fastconst_ns
        double slowconst_ns
        double nspersample
        CFDiscConfig cfdconfig

