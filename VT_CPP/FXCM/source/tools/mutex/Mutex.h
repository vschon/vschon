// Copyright [2014] <Brandon>

#pragma once

#if !defined(WIN32) && !defined(PTHREADS_MUTEX)
// if in linux and pthread is not defined, than define pthread_mutex
// if in windows, than not defining pthread_mutex
    #define PTHREADS_MUTEX
#endif

#ifdef PTHREADS_MUTEX
    #include <pthread.h>
#endif

namespace tools {
    class GSTOOLS3 Mutex {
     public:
        Mutex();
        ~Mutex();
        void lock();
        void unlock();

        class Lock {
         public:
            Lock(Mutex& m) : mutex(&m) {
                // pass by reference, get the address of m
                mutex->lock();
            }
            Lock(Mutex* m) : mutex(m) {
                mutex->lock();
            }
            ~Lock() {
                mutex->unlock();
            }
         private:
            Mutex* mutex;
        };

     private:
     #ifdef PTHREADS_MUTEX
        pthread_mutex_t m_oMutex;
     #else
        // CRITICAL_SECTION m_oCritSection;
     #endif
    };
}// namespace tools
