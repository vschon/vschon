// Copyright [2014] <Brandon>
#pragma once

#include <string>

class SessionStatusListener : public IO2GSessionStatus {
 private:
     long mRefCount;
     /*subsession identifier */
     std::string mSessionID;
     /*PIN code */
     std::string mPin;
     /*Error flag */
     bool mError;
     /*Flag Connected*/
     bool mConnected;
     /*Flag Disconnected*/
     bool mDisconnected;
     /*Flag print session*/
     bool mPrintSubsessions;

     /*session object*/
     IO2GSession *mSession;
     void* mSessionEvent;

 protected:
     ~SessionStatusListener();

 public:
     /* constructor 
      @param session              session to listen to
      @param printSubsession      To print subsession or not
      @param sessionID            Identifier of subsession
      @param pin                  Pind code
     */
     SessionStatusListener(IO2GSession *session, bool printSubsessions,
             const char *sessionID = 0, const char *pin = 0);

     virtual long addRef();
     virtual long release();

     /*Callback when login failed*/
     virtual void onLoginFailed(const char *error);
     /*Callback when sesssion status changed*/
     /*IO2GSessionStatus::O2GSessionStatus is a enum
      * indicating state of session
      */
     virtual void onSessionStatusChanged(IO2GSessionStatus::O2GSessionStatus status);
     bool hasError() const;
     bool isConnected() const;
     bool isDisconnected() const;
    
     /*reset error information before login/logout*/
     bool reset();

     /*wait for connection or error*/
     bool waitEvents();
};
