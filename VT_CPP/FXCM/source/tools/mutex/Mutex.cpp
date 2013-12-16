// Copyright [2014] <Brandon>

#include "../tools_stdafx.h"
#include "Mutex.h"

using namespace tools;

Mutex::Mutex() {
#ifdef PTHREAD_MUTEX
    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_RECURSIVE);
    pthread_mutex_init(&m_oMutex, &attr);
    pthread_mutexattr_destroy(&attr);
#else
    // TODO: ocritsection
#endif
}

Mutex::~Mutex() {
#ifdef PTHREAD_MUTEX
    pthread_mutex_destroy(&m_oMutex);
#else
    // TODO: ocritsection
#endif
}

void Mutex::lock() {
#ifdef PTHREAD_MUTEX
    pthread_mutex_lock(&m_oMutex);
#endif
}

void Mutex::unlock() {
#ifdef PTHREAD_MUTEX
    pthread_mutex_unlock(&m_oMutex);
#endif
}
