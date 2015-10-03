cimport cython
from libcpp.vector cimport vector

cdef extern from "Flash.hh" namespace "subevent":
    cdef cppclass Flash:
        Flash() except +
        int ch
        int tstart
        int tend
        int tmax
        double maxamp
        double area
        vector[double] expectation
        vector[double] waveform

cdef extern from "FlashList.hh" namespace "subevent":
    cdef cppclass FlashList:
        FlashList() except +
        int add( Flash&& flash )
        Flash& get( int i )
        int size()
        void clear()
        void sortByTime()
        void sortByCharge()
        void sortByAmp()
        bint sortedByTime()
        bint sortedbyCharge()
        bint sortedByAmp()

cdef extern from "WaveformData.hh" namespace "subevent":
    cdef cppclass WaveformData:
        WaveformData() except +
        vector[double]& get( int channel )
        void set( int channel, vector[double]& wfm )
        
