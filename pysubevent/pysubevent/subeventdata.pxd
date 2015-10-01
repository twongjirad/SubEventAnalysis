cimport cython
from libcpp.vector cimport vector

cdef extern from "Flash.hh" namespace "subevent":
    cdef cppclass Flash:
        Flash() except +
        int ch
        int tstart
        int tend
        int tmax
        float maxamp
        vector[double] expectation
        vector[double] waveform
