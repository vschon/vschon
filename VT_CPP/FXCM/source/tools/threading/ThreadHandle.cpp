//copyright 2013 Brandon

#include "../tools_stdafx.h"
#include "ThreadHandle.h"
#include "AThread.h"

using tools::ThreadHandle;
using tools::AThread;

ThreadHandle::ThreadHandle()
    : mHandle(getCurrentThreadHandle()) {}

ThreadHandle::ThreadHandle(Handle handle)
    : mHandle(handle) {}

ThreadHandle::~ThreadHandle() {}

ThreadHandle* ThreadHandle::getCurrentThread() {
    //can only get a thread from this static method
    return new ThreadHandle();
}

void ThreadHandle::release() {
    delete this;
}

bool ThreadHandle::isCurrentThread() const {
    return pthread_equal(mHandle, pthread_self());
}

bool ThreadHandle::equals(ThreadHandle const *threadHandle) const {
    if (!threadHandle)
        return false;
    return pthread_equal(mHandle, threadHandle->mHandle);
}

bool ThreadHandle::equals(AThread const *thread) const {
    if (!thread)
        return false;
    return equals(thread->getHandle());
}

ThreadHandle::Handle ThreadHandle::getCurrentThreadHandle() const {
    //return the ID of current(calling) thread
    return pthread_self();
}


ThreadHandle::Handle ThreadHandle::getHandle() const {
    return mHandle;
}

void ThreadHandle::setHandle(ThreadHandle::Handle handle) {
    mHandle = handle;
}
