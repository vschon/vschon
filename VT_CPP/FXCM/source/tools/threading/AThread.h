// copyright 2013 Brandon

#pragma once

#if !defined(WIN32) && !defined(PTHREADS)
#   define PTHREADS
#endif

#ifndef INFINITE
#   define INFINITE        0xFFFFFFFF    // Infinite timeout
#endif

#define THREAD_OBJECT_HAS_DELETED 0xFFFFFFFE

#include "Mutex.h"
#include "ThreadHandle.h"

#ifdef PTHREADS
    #include "PosixCondVarWrapper.h"
#endif

namespace tools {

 /**
 @class AThread
 Wrapper for platform-dependend threads implementation.
*/
class GSTOOLS3 AThread
{
 public:
    typedef enum {
        PriorityUnknown = -1,
        PriorityError = 0,
        PriorityLow = 1,
        PriorityNormal = 2,
        PriorityHigh = 3,
        PriorityDefault = 4
    } PriorityLevel;

 public:
    /**
     Default constructor.
    */
    AThread();

    /**
     Destructor.
    */
    virtual ~AThread();

    /**
     Returns a handle of the thread.
     @return Returned object is owned by AThread. Returned value MUST not be removed.
    */
    ThreadHandle const *getHandle() const;

    /**
     Creates a new thread.
     @return If the function succeeds or thread is already created by previous call, the returned value is true.
             If the function fails, the returned value is false.
    */
    bool start();

    /**
     Waits for the thread to terminate.
     @param waitMilliseconds - the time-out interval, in milliseconds.
            The function returns if the interval elapses, even if the tread state is running.
            If waitMilliseconds is zero, the function tests the thread's state and returns immediately.
            If waitMilliseconds is INFINITE, the function's time-out interval never elapses.
     @return If the function succeeds (the thread is terminated), the return value is true.
             If the function fails or the interval elapses, the return value is false.
    */
    bool join(unsigned long waitMilliseconds = INFINITE);

    /**
     Sets a terminate flag.
    */
    void requestStop();

    /**
     Returns terminate flag state.
     @return If terminate flag is set, return true.
             If terminate flag is not set, return false.
    */
    bool isStopRequested() const;

    /**
     Returns the thread status.
     @return If thread is running, return true.
             If thread is stopped, return false.
    */
    bool isRunning() const;

    /**
     Get thread priority.
    */
    PriorityLevel getPriority() const;

    /**
     Set thread priority.
    */
    bool setPriority(PriorityLevel ePrior);

 protected:
    virtual int run() = 0;

    #ifdef PTHREADS
        static void *threadRunner(void *param);
        static void threadCleanup(void *param);
    #elif WIN32
        static unsigned int WINAPI threadRunner(void *param);
    #endif

 private:
    volatile bool mIsStopRequested;
    ThreadHandle mHandle;
    mutable Mutex mAccessMutex;
    int mDefaultPriority;

    #ifdef PTHREADS
        volatile bool mIsCreated;
        //pthread_mutex_t mCondMutex;
        //pthread_cond_t mCondVar;
        PosixCondVar *mCondVar;
    #elif WIN32
        HANDLE mThread;
    #endif 
};


}// namespace tools
