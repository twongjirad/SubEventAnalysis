# cython: profile=True

import numpy as np
cimport numpy as np

DTYPEUINT16 = np.uint16
ctypedef np.uint16_t DTYPEUINT16_t
DTYPEINT16 = np.int16
ctypedef np.int16_t DTYPEINT16_t
DTYPEFLOAT32 = np.float32
ctypedef np.float32_t DTYPEFLOAT32_t

DTYPE = np.float
ctypedef np.float_t DTYPE_t


cpdef runCFdiscriminator( np.ndarray[DTYPE_t, ndim=1] waveform, int delay, int threshold, int deadtime, int width ):
  """
  inputs:
  -------
  waveform: raw adc waveform
  delay: subtraction time delay in ticks
  threshold: to form disc. fire
  deadtime: ticks to wait before new disc. can form
  width: length of tick window to find max adc counts
  """

  cdef np.ndarray[DTYPE_t, ndim=1] diff = np.zeros( len(waveform), dtype=DTYPE )
  t_fire = []
  amp_fire = []
  maxt_fire = []
  last_fire = -1
  for tdc in range( delay, len(waveform)-delay ):
      diff[tdc] = waveform[tdc]-waveform[tdc+delay]
      
  # determine time
  for t in range(0,len(waveform)):
      if diff[t]>threshold and ( len(t_fire)==0 or (len(t_fire)>0 and t_fire[-1]+deadtime<t) ):
          t_fire.append( t-delay )
  # determine max amp
  for trig in t_fire:
      amp_fire.append( np.max( waveform[trig:np.minimum( len(waveform), trig+width )] )  )
      maxt_fire.append( trig+np.argmax( waveform[trig:np.minimum( len(waveform), trig+width )] ) )

  return zip( t_fire, amp_fire, maxt_fire )


# NATIVE C++
from libcpp.vector cimport vector

cdef extern from "cfdiscriminator.hh" namespace "cpysubevent":
   cdef void runCFdiscriminatorCPP( vector[ int ]& t_fire, vector[ int ]& amp_fire, vector[ int ]& maxt_fire,
                                    double* waveform, int delay, int threshold, int deadtime, int width, int arrlen )
                                   

cpdef pyRunCFdiscriminatorCPP( np.ndarray[DTYPE_t, ndim=1] waveform, int delay, int threshold, int deadtime, int width ):
  """
  inputs:
  -------
  waveform: raw adc waveform
  delay: subtraction time delay in ticks
  threshold: to form disc. fire
  deadtime: ticks to wait before new disc. can form
  width: length of tick window to find max adc counts
  """
  cdef vector[int] t_fire
  cdef vector[int] amp_fire
  cdef vector[int] maxt_fire
  runCFdiscriminatorCPP( t_fire, amp_fire, maxt_fire, <double*>waveform.data, delay, threshold, deadtime, width, len(waveform) )
  return zip( t_fire, amp_fire, maxt_fire )
      
