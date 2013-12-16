// copyright 2013 Brandon

#pragma once

#if !defined(WIN32) && !defined(PTHREADS)
#   define PTHREADS
#endif

#ifdef PTHREADS
    #include <pthread.h>
#endif

namespace tools
{

class AThread; // wrapper of threadhandle

/**
 @class AThread
 Wrapper for platform-dependend threads identification.
*/


class GSTOOLS3 ThreadHandle{
    //It is a wrapper of pthread_t
    typedef pthread_t Handle;
    friend class AThread;
 private:
    // private constructor can only be used 
    // within the class
    ThreadHandle();
    ThreadHandle(Handle handle);
    ~ThreadHandle();
 public:
    /**
     Create new instance of current thread.
     @return Return new instance of current thread.
    */
    static ThreadHandle* getCurrentThread();

    /**
     Destroy object.
    */
    void release();

    /**
     Compare thread handle with caller's thread.
     @return If current thread handle and caller's thread are the same, return true.
             If current thread handle and caller's thread are different, return false.
    */
    bool isCurrentThread() const;

    /**
     Complate two thread handles.
     @param threadHandle - target thread handle.
     @return If current thread handle and target thread handle are the same, return true.
             If current thread handle and target thread handle are different, return false.
    */
    bool equals(ThreadHandle const *threadHandle) const;

    /**
     Compare current thread handle with target thread.
     @param thread - target thread.
     @return If current thread handle and the target thread handle are the same, retur true.
             If current thread handle and the target thread handle are different, return false.
    */
    bool equals(AThread const *thread) const;

 private:
    Handle getCurrentThreadHandle() const;
    Handle getHandle() const;
    void setHandle(Handle handle);

 private:
    Handle mHandle;
};

}// namespace tools



