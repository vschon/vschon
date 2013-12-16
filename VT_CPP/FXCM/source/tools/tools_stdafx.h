// Copyright [2014] <Brandon>
// include file for standard system files or project specific include files

#pragma once

#ifdef WIN32
#   ifndef WINVER
#       define WINVER 0x501
#   endif
#else
#   define PTHREADS
#   define PTHREADS_MUTEX
#endif

#ifdef WIN32
#   define GSTOOLS3 __declspec(dllexport)
#else
    #define GSTOOLS3
    #include <sys/types.h>  // various data types
    #include <sys/stat.h>   // file information
    #include <unistd.h>     // access to POSIX operation API
    #include <errno.h>     // report error conditions
    #include <dirent.h>     // for directory traversing
#endif

// TODO: additional project specific headers
