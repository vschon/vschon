// copyright 2013 Brandon

#include "../tools_stdafx.h"
#include <cstdio>
#include "hidden_class.h"
#ifdef PTHREADS
#include <set>
#include <string>
#include <sys/timeb.h>
#include "winEmul.h"
#include "CWinEventHandle.h"

using std::wstring;
// static before class mean there cannot be any instance of the class
// recursive mutex means the same thread can lock the object twice

static class HIDDEN_CLASS CCriticalSection
{
  pthread_mutex_t m_Mutex;
public:
  CCriticalSection(bool recursive = true)
  {
    if (recursive)
    {
      //create a p_mutex_attr_t
      pthread_mutexattr_t attr;
      //initialize it
      pthread_mutexattr_init(&attr);
      //set it to be recursive
      pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_RECURSIVE);
      //use the attr to initialzie the mutex
      pthread_mutex_init(&m_Mutex, &attr);
    }
    else
    {
      pthread_mutex_init(&m_Mutex, 0);
    }
  }
  ~CCriticalSection()
  {
    pthread_mutex_destroy(&m_Mutex);
  }
  inline void enter() { pthread_mutex_lock(&m_Mutex); }
  inline void leave() { pthread_mutex_unlock(&m_Mutex); }
} s_CritSect;


class HIDDEN_CLASS CEventLock
{
public:
  CEventLock() { s_CritSect.enter(); }
  ~CEventLock() { s_CritSect.leave(); }
};

typedef std::set<CWinEventHandle*> TWinEventHandleSet;
TWinEventHandleSet s_Set;

class HIDDEN_CLASS CWinEventHandleSet{
 public:
     static CBaseHandle* createEvent(bool manualReset, bool signaled,
             const wchar_t* name) {
        //create an event and insert it into the s_Set
        CWinEventHandle* handle(new CWinEventHandle(manualReset, signaled, name));
        CEventLock lock;
        s_Set.insert(handle);
        return handle;
     }
     static void closeHandle(CWinEventHandle* eventHandle){
        // delete an event and remove it from the s_Set
        CEventLock lock;
        if (eventHandle->decRefCount() == 0) {
            s_Set.erase(eventHandle);
            delete eventHandle;
        }
     }

     static HANDLE openEvent(const wchar_t* name){
        //retrieve the event from s_set
        CEventLock lock;
        for (TWinEventHandleSet::iterator iter(s_Set.begin());
                iter != s_Set.end(); iter++){
            if ((*iter)->name() == name){
                (*iter)->incRefCount();
                 return *iter;
            }
        }
     }
};

bool CWinEventHandle::close(){
    // a method of CWinEventHandle, impleneted here
    // because the CWinEventHandleSet is only defined here
    CWinEventHandleSet::closeHandle(this);
    return true;
}


inline CWinEventHandle* castToWinEventHandle(HANDLE hEvent){
    return (CWinEventHandle*) (hEvent);
}


/* PLEASE REFER TO MSDN 
 * FOLLOWING FUNC MIMICS THE WINAPI EVENTS
 */

DWORD WINAPI GetTickCount(){
    struct timeb currSysTime;
    ftime(&currSysTime);
    return long(currSysTime.time) * 1000 + currSysTime.millitm;
}

void WINAPI Sleep(DWORD dwMilliseconds)
{
    usleep(1000 * dwMilliseconds);
}

HANDLE WINAPI CreateEventW(LPSECURITY_ATTRIBUTES, BOOL bManualReset,
        BOOL bInitialState, LPCWSTR lpName){
    return CWinEventHandleSet::createEvent(bManualReset != FALSE,
            bInitialState != FALSE, lpName);
}

HANDLE WINAPI OpenEventW(DWORD dwDesiredAccess, BOOL bInheritHandle, LPCWSTR lpName)
{
  return CWinEventHandleSet::openEvent(lpName);
}

BOOL WINAPI CloseHandle(HANDLE handle) {
    // if successful, return non-zero
    // otw, return zero
    bool ret(false);
    if (handle != NULL){ 
        CBaseHandle* baseHandle(static_cast<CBaseHandle*>(handle));
        if (!baseHandle->close())
            printf("Closing unknown HANDLE type\n");
        ret = true;
    }
    return ret;
}


BOOL WINAPI SetEvent(HANDLE hEvent) {
    //set the event to signaled state
    CEventLock lock; //The lock avoids a race condition with subscribe() in WaitForMultipleObjects()//
    castToWinEventHandle(hEvent)->signal();
    return true;
}

BOOL WINAPI ResetEvent(HANDLE hEvent) {
    castToWinEventHandle(hEvent)->reset();
    return true;
}

BOOL WINAPI PulseEvent(HANDLE hEvent) {
    return castToWinEventHandle(hEvent)->pulse();
}

DWORD WINAPI WaitForSingleObject(HANDLE obj, DWORD timeMs) {
    CBaseHandle* handle(static_cast<CBaseHandle*>(obj));
    if (handle->wait(timeMs))
        //WAIT_OBECT_0: state signaled
        return WAIT_OBJECT_0;
    // Might be handle of wrong type?
    return WAIT_TIMEOUT;
}

DWORD WINAPI WaitForMultipleObjects(DWORD numObj, const HANDLE* objs, BOOL waitAll, DWORD timeMs) {
  CWinEventHandle* eventHandle[MAXIMUM_WAIT_OBJECTS];
  //assert(numObj <= MAXIMUM_WAIT_OBJECTS);
  if (waitAll)
  {
    const DWORD startMs(GetTickCount());
    for (unsigned ix(0); ix < numObj; ix++)
    {
      // Wait for all events, one after the other.
      CWinEventHandle* event(castToWinEventHandle(objs[ix]));
      //assert(event);
      DWORD usedMs(GetTickCount() - startMs);
      if (usedMs > timeMs)
      {
        return WAIT_TIMEOUT;
      }
      if (!event->wait(timeMs - usedMs))
      {
        return WAIT_TIMEOUT;
      }
    }
    return WAIT_OBJECT_0;
  }
  s_CritSect.enter();//
  // Check whether any event is already signaled
  for (unsigned ix(0); ix < numObj; ix++)
  {
    CWinEventHandle* event(castToWinEventHandle(objs[ix]));
    //assert(event);
    if (event->signaled())
    {
      event->resetIfAuto(); // Added 13.09.2008 (bug detected by BRAD H)
      s_CritSect.leave();//
      return ix;
    }
    eventHandle[ix] = event;
  }
  if (timeMs == 0)
  {
    // Only check, do not wait. Has already failed, see above.
    s_CritSect.leave();//
    return WAIT_TIMEOUT;
  }
  /***************************************************************************
  Main use case: No event signaled yet, create a subscriber event.
  ***************************************************************************/
  CWinEventHandle subscriberEvent(false, 0);
  // Subscribe at the original objects
  for (unsigned ix(0); ix < numObj; ix++)
  {
    eventHandle[ix]->subscribe(&subscriberEvent);
  }
  s_CritSect.leave(); // Re-enables SetEvent(). OK since the subscription is done

  bool success(subscriberEvent.wait(timeMs));

  // Unsubscribe and determine return value
  DWORD ret(WAIT_TIMEOUT);
  s_CritSect.enter();//
  for (unsigned ix(0); ix < numObj; ix++)
  {
    if (success && eventHandle[ix]->signaled())
    {
      success = false;
      ret = ix;
      // Reset event that terminated the WaitForMultipleObjects() call
      eventHandle[ix]->resetIfAuto(); // Added 16.09.2009 (Alessandro)
    }
    eventHandle[ix]->unSubscribe(&subscriberEvent);
  }
  s_CritSect.leave();//
  return ret;
}




#endif
