// copyright 2014 Brandon

#ifndef CWINEVENTHANDLE_H
#define CWINEVENTHANDLE_H

#include "hidden_class.h"

class HIDDEN_CLASS CBaseHandle {
 public:
     CBaseHandle() {}
     virtual ~CBaseHandle() {}
     virtual bool wait(unsigned numMs) {return false;}
     virtual bool close() {return false;}
};

class HIDDEN_CLASS CWinEventHandle : public CBaseHandle {
 public:
     CWinEventHandle(bool manualReset = false, bool signaled = false,
            const wchar_t* name = NULL);
     virtual ~CWinEventHandle();
     bool close();
     void incRefCount();
     int decRefCount();
     bool signaled() const {return m_Signaled;}
     std::wstring name() const {return m_Name;}
     void reset();
     void signal();
     bool pulse();
     bool wait(unsigned numMs);
     bool wait();
     void subscribe(CWinEventHandle* subscriber);
     void unSubscribe(CWinEventHandle* subscriber);
     bool isManualReset() const {return m_ManualReset;}
     void resetIfAuto();
 private:
     pthread_mutex_t m_Mutex;
     pthread_mutex_t m_SubscrMutex;
     pthread_cond_t m_Cond;
     volatile bool m_ManualReset;
     volatile bool m_Signaled;
     volatile long m_Count;
     volatile long m_RefCount;
     std::wstring m_Name;
     std::set<CWinEventHandle*> m_Subscriber;
};

#endif
