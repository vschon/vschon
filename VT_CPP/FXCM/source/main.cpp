// Copyright

#include <cstring>

#include <string>

#include "login/login.h"

int main() {

    /*Login*/
    LoginParams *loginParams = new LoginParams();
    loginParams->setLogin("D172198296001");
    loginParams->setPassword("7226");
    loginParams->setURL("http://www.fxcorporate.com/Hosts.jsp");
    loginParams->setConnection("Demo");
}
