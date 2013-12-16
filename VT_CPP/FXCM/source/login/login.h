// Copyright [2014] <Brandon>

#pragma once
#include <string>

class LoginParams {
/*Used to store the login parameters*/
 public:
    class Strings {
     public:
         static const char *loginNotSpecified;
         static const char *passwordNotSpecified;
         static const char *connectionNotSpecified;
         static const char *urlNotSpecified;
    };

 public:
    LoginParams();
    ~LoginParams(void);

    void setLogin(std::string);
    void setPassword(std::string);
    void setURL(std::string);
    void setConnection(std::string);
    void setSessionID(std::string);
    void setPin(std::string);

    const char *getLogin();
    const char *getPassword();
    const char *getURL();
    const char *getConnection();
    const char *getSessionID();
    const char *getPin();

 private:
    const char *getArgument(int, char **, const char *);
    std::string mLogin;
    std::string mPassword;
    std::string mURL;
    std::string mConnection;
    std::string mSessionID;
    std::string mPin;
};
