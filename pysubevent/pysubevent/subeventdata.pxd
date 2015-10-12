cimport cython
from libcpp.vector cimport vector
from libcpp.string cimport string

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

cdef extern from "SubEvent.hh" namespace "subevent":
    cdef cppclass SubEvent:
        SubEvent() except +
        int tstart_sample
        int tend_sample
        double tstart_ns
        double tend_ns
        double totpe
        double maxamp
        FlashList flashes

cdef extern from "SubEventList.hh" namespace "subevent":
    cdef cppclass SubEventList:
        SubEventList() except +
        int add( SubEvent&& flash )
        SubEvent& get( int i )
        int size()
        void clear()
        void sortByTime()
        void sortByCharge()
        void sortByAmp()
        bint sortedByTime()
        bint sortedByCharge()
        bint sortedByAmp()

cdef extern from "WaveformData.hh" namespace "subevent":
    cdef cppclass WaveformData:
        WaveformData() except +
        vector[double]& get( int channel )
        void set( int channel, vector[double]& wfm, bint islowgain )
        void setLowGain( int channel, bint islowgain )
        bint isLowGain( int channel )


cdef extern from "SubEventIO.hh" namespace "subevent":
    cdef cppclass SubEventIO:
        SubEventIO( string filename, string mode )
        int eventid
        int nsubevents
        double chmaxamp
        void transferSubEventList( SubEventList* subevents )
        void write()
        void fill()
        void clearlist()
