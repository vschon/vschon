from __future__ import division
import numpy as np
cimport numpy as np
from libc.math cimport exp

#Use cython to calculate R matrix

def getR11(long N,double beta1,np.ndarray[np.float64_t, ndim=2] pos):
    cdef np.ndarray[np.float64_t, ndim = 2] R11 = np.zeros((N,1),dtype = np.float64)
    cdef int i
    for i in range(1,N):
        R11[i,0] = (1+R11[i-1,0])*exp(-beta1*(pos[i,0]-pos[i-1,0]))
    return R11

def getR12(long N, long M, double beta1, np.ndarray[np.float64_t, ndim =2] pos, np.ndarray[np.float64_t, ndim = 2] neg):
    cdef np.ndarray[np.float64_t, ndim =2] R12 = np.zeros((N,1),dtype = np.float64)
    cdef int i,j
    cdef double tempsum = 0.0
    for i in range(1,N):
        tempsum = 0.0
        for j in range(M):
            if neg[j,0] >= pos[i,0]:
                break
            if neg[j,0] >= pos[i-1,0] and neg[j,0] < pos[i,0]:
                tempsum += exp(-beta1*(pos[i,0] - neg[j,0]))
        R12[i,0] = R12[i-1,0]*exp(-beta1*(pos[i,0]-pos[i-1,0])) + tempsum
    return R12

def getR21(long N,long M, double beta2, np.ndarray[np.float64_t, ndim = 2] pos,np.ndarray[np.float64_t, ndim = 2] neg):
    cdef np.ndarray[np.float64_t, ndim = 2] R21 = np.zeros((M,1),dtype = np.float64)
    cdef int i,j
    cdef double tempsum = 0.0
    for j in range(1,M):
        tempsum=0.0
        for i in range(N):
            if pos[i,0] > neg[j,0]:
                break
            if pos[i,0] >= neg[j-1,0] and pos[i,0] < neg[j,0]:
                tempsum += np.exp(-beta2*(neg[j,0]-pos[i,0]))
        R21[j,0] = R21[j-1,0]*np.exp(-beta2*(neg[j,0]-neg[j-1,0])) + tempsum
    return R21

def getR22(long M, double beta2,np.ndarray[np.float64_t, ndim =2] neg):
    cdef np.ndarray[np.float64_t, ndim = 2] R22 = np.zeros((M,1),dtype = np.float64)
    cdef int j
    for j in range(1,M):
        R22[j,0] = (1+R22[j-1,0])*np.exp(-beta2*(neg[j,0]-neg[j-1,0]))
    return R22


