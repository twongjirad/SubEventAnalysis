
from subeventdata cimport SubEvent

cdef class pySubEvent:
    cdef bint __isowner
    cdef SubEvent* thisptr

