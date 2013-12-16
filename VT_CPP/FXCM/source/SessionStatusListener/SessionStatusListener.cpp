// Copyright [2004] <Brandon>

#include <ForexConnect.h>
#include "SessionStatusListener.h"

SessionStatusListener::SessionStatusListener(IO2GSession *session,
        bool printSubsessions, const char *sessionID, const char *pin) {

    if (sessionID != 0)
        mSessionID = sessionID;
    else
        mSessionID = "";
    if (pin != 0)
        mPin = pin;
    else
        mPin = "";
    mSession = session;
    mSession->addRef();
    reset();
    mPrintSubsessions = printSubsessions;
    mRefCount = 1;
    /*TODO Understand CreateEvent*/
    mSessionEvent = CreateEvent(0, )

}

