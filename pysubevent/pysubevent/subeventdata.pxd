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
        double area30
        vector[double] expectation
        vector[double] waveform

cdef extern from "FlashList.hh" namespace "subevent":
    cdef cppclass FlashList:
        FlashList() except +
        int add( Flash&& flash )
        void transferFlash( Flash& flash )
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
        double pe30
        double totpe
        double pe30_1
        double totpe_1
        double maxamp
        FlashList flashes
        FlashList flashes_pass2
        void transferFlashes( FlashList& flashes )

cdef extern from "SubEventList.hh" namespace "subevent":
    cdef cppclass SubEventList:
        SubEventList() except +
        int add( SubEvent&& subevent )
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
        vector[double]& getbaseline( int channel )
        void set( int channel, vector[double]& wfm, bint islowgain )
        void setLowGain( int channel, bint islowgain )
        bint isLowGain( int channel )
        void storeTimeInfo( int ch, unsigned int frame, double timestamp )
        void calcBaselineInfo()

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

cdef extern from "CosmicWindowSubEvents.hh" namespace "subevent":
    cdef cppclass CosmicWindowHolder:
        CosmicWindowHolder() except +
        void addHG( int ch, int t_sample, vector[double] wfm )
        void addLG( int ch, int t_sample, vector[double] wfm )
        
