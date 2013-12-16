// Copyright

#pragma once
#include "login.h"

#include <string.h>
#include <cstring>

const char *LoginParams::Strings::loginNotSpecified = "'Login' is not specified (/l|-l|/login|--login)";
const char *LoginParams::Strings::passwordNotSpecified = "'Password' is not specified (/p|-p|/password|--password)";
const char *LoginParams::Strings::urlNotSpecified = "'URL' is not specified (/u|-u|/url|--url)";
const char *LoginParams::Strings::connectionNotSpecified = "'Connection' is not specified (/c|-c|/connection|--connection)";

/*Constructor*/
LoginParams::LoginParams(){}

/*Destructor*/
LoginParams::~LoginParams(void){}


const char *LoginParams::getArgument(int argc, char **argv, const char *key){
    for (int i = 1; i<argc; ++i){
        /*search for every '-'*/
        if (argv[i][0] == '-'){
            int iDelimOffset = 0;
            if (strncmp(argv[i],"-",1) == 0)
                /*if the string matches '-'*/
                iDelimOffset = 1;
            if (strcmp(argv[i] + iDelimOffset, key) == 0 && argc > i+1)
                /*if the char after - matches key*/ 
                return argv[i+1];
        }
    } 
    return "";
}

void LoginParams::setLogin(std::string login){
    mLogin = login; 
}

void LoginParams::setPassword(std::string password){
    mPassword = password;
}

void LoginParams::setURL(std::string url){
    mURL = url;
}

void LoginParams::setConnection(std::string connection){
    mConnection = connection;
}

void LoginParams::setSessionID(std::string sessionID){
    mSessionID = sessionID;
}

void LoginParams::setPin(std::string pin){
    mPin = pin;
}

const char *LoginParams::getLogin(){
    return mLogin.c_str();
}

const char *LoginParams::getPassword(){
    return mPassword.c_str();
}

const char *LoginParams::getURL(){
    mURL.c_str();
}

const char *LoginParams::getConnection(){
    return mConnection.c_str();
}

const char *LoginParams::getSessionID(){
    return mSessionID.c_str();
}

const char *LoginParams::getPin(){
    return mPin.c_str();
}
