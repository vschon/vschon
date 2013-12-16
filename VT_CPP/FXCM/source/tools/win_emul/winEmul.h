// Copyright 2014 Brandon

#pragma once

#ifndef WINEMUL_H
    #define WINEMUL_H
    #ifndef PTHREADS
        #define PTHREADS
    #endif  
    #define WINBASEAPI
    #define CONST const
    #define STATUS_WAIT_0       ((DWORD)0x00000000L)
    #define STATUS_TIMEOUT      ((DWORD)0x00000102L)
    #ifndef _WINDEF_
        #define WINAPI
        #ifndef FALSE
            #define FALSE       0
        #endif
    #endif
    #define stdext __gnu_cxx
    #define _WINDEF_
    #define WINAPI
    #ifndef FALSE
        #define FALSE           0
    #endif
    #ifndef TRUE
        #define TRUE            1
    #endif

// still continue the emulation of windows in linux
typedef unsigned long       ULONG_PTR, DWORD, DWORD_PTR, *LPDWORD, COLORREF, *LPCOLORREF;
typedef int                 BOOL, *LPBOOL, errno_t;
typedef unsigned char       BYTE, *LPBYTE;
typedef unsigned short      WORD, *LPWORD;
typedef int                 INT, *LPINT;
typedef long                LONG, *LPLONG, HRESULT;
typedef void                *LPVOID, *HINTERNET, *HANDLE, *HMODULE, *HINSTANCE;
typedef const void          *LPCVOID;
typedef unsigned int        UINT, *PUINT;
typedef char                *LPSTR, *LPTSTR;
typedef const char          *LPCSTR, *LPCTSTR;
typedef wchar_t             WCHAR, *PWCHAR, *LPWCH, *PWCH, *LPWSTR, *PWSTR;
typedef const WCHAR         *LPCWCH, *PCWCH, *LPCWSTR, *PCWSTR;

// redefine members in linux compiler to windows compiler name
    #       define MAX_PATH            260
    #       define CALLBACK
    #       define RGB(r, g, b)          ((COLORREF)(((BYTE)(r)|((WORD)((BYTE)(g)) << 8))|(((DWORD)(BYTE)(b)) << 16)))

    #       define _int8 char
    #       define _int16 short
    #       define _int32 int
    #       define __int64 long long
    #       define _int64 long long

    #       define _strdup(A) strdup(A)
    #       define _wcsdup(A) wcsdup(A)
    #       define memcpy_s(A, B, C, D) memcpy(A, C, D)
    #       define _stricmp(A, B) strcasecmp(A, B)
    #       define sprintf_s(A, B, args...) sprintf(A, ## args)
    #       define fprintf_s(A, B, args...) fprintf(A, B, ## args)
    #       define sscanf_s(A, B, args...) sscanf(A, B, ## args)
    #       define _close(A) close(A)
    #       define _read(A, B, C) read(A, B, C)
    #       define _write(A,B,C) write(A,B,C)
    #       define _lseek(A,B,C) lseek(A,B,C)
    #       define _itoa_s(A,B,C,D) itoa(A,B,D)
    #       define _vsnprintf_s(buffer,sizeOfBuffer,count,format,args) vsprintf(buffer,format,args)
    #       define vfprintf_s(A,B,C) vfprintf(A,B,C)
    #       define _ftime(A) ftime(A)
    #       define _timeb timeb
    #       define localtime_s(A,B) localtime_r(B,A)
    #       define _threadid (unsigned long)0

    #       define _O_BINARY 0
    #       define _O_TEXT 0
    #       define _O_CREAT O_CREAT
    #       define _O_APPEND O_APPEND
    #       define _O_EXCL O_EXCL
    #       define _O_RDONLY O_RDONLY
    #       define _O_WRONLY O_WRONLY
    #       define _SH_DENYNO 0x666
    #       define _SH_DENYRW S_IRUSR|S_IWUSR
    #       define _S_IWRITE S_IWUSR //S_IWUSR|S_IWGRP|S_IWOTH
    #       define _S_IREAD S_IRUSR //S_IRUSR|S_IRGRP|S_IROTH
    #       define VER_SEP_DOT   .
    #       define VER_STR_HELPER4(x,y,z,b,sep) #x #sep #y #sep #z #sep #b 
    #       define S_OK       ((HRESULT)0x00000000L)

static const DWORD MAXIMUM_WAIT_OBJECTS(32);

    #ifndef _WINBASE_
        #define WAIT_TIMEOUT    STATUS_TIMEOUT
        #define WAIT_OBJECT_0   ((STATUS_WAIT_0 ) + 0 )
        #define CREATE_SUSPENDED 0x00000004
        #ifndef INFINITE
            #define INFINITE        0xFFFFFFFF    // Infinite timeout
        #endif//INFINITE

typedef struct _SECURITY_ATTRIBUTES {
    BOOL bInheritHandle;
} SECURITY_ATTRIBUTES;
typedef SECURITY_ATTRIBUTES* LPSECURITY_ATTRIBUTES;

        #ifndef CreateEvent
            #define CreateEvent CreateEventW
        #endif
        #ifndef OpenEvent
            #define OpenEvent OpenEvnetW
        #endif
    #endif

    #ifdef PTHREADS
        #include <stdio.h>
namespace tools {
    namespace win_emul {
        // declaration of functions
        DWORD GSTOOLS3 WaitForSingleObject(HANDLE hHandle, DWORD dwMilliseconds);
        DWORD GSTOOLS3 WaitForMultipleObjects(DWORD nCount, CONST HANDLE *lpHandles, BOOL bWaitAll, DWORD dwMilliseconds);
        BOOL GSTOOLS3 SetEvent(HANDLE hEvent);
        BOOL GSTOOLS3 ResetEvent(HANDLE hEvent);
        BOOL GSTOOLS3 PulseEvent(HANDLE hEvent);  // Used in CRsEvent.cpp

        HANDLE GSTOOLS3 CreateEventW(LPSECURITY_ATTRIBUTES lpEventAttributes, BOOL bManualReset, BOOL bInitialState, LPCWSTR lpName);

        HANDLE GSTOOLS3 OpenEventW(DWORD dwDesiredAccess, BOOL bInheritHandle, LPCWSTR lpName);
        BOOL GSTOOLS3 CloseHandle(HANDLE hObject);

        DWORD GSTOOLS3 GetTickCount();
        void GSTOOLS3 Sleep(DWORD dwMilliseconds);

        errno_t GSTOOLS3 fopen_s(FILE** pFile, const char *filename, const char *mode);
        errno_t GSTOOLS3 _sopen_s(int* pfh, const char *filename, int oflag, int shflag, int pmode);
        errno_t GSTOOLS3 _strlwr_s(char * str, size_t numberOfElements);
        errno_t GSTOOLS3 _strupr_s(char * str, size_t numberOfElements);
        errno_t GSTOOLS3 freopen_s(FILE** pFile, const char *path, const char *mode, FILE *stream);
        errno_t GSTOOLS3 strcpy_s(char *strDest, size_t numberOfElements, const char *strSource);
        errno_t GSTOOLS3 strncpy_s(char *strDest, size_t numberOfElements, const char *strSource, size_t count);
        errno_t GSTOOLS3 strcat_s(char *strDest, size_t numberOfElements, const char *strSource);
    }// namespace win_emul
}// namespace tools


        #       define WaitForSingleObject(A,B) tools::win_emul::WaitForSingleObject(A,B)
        #       define WaitForMultipleObjects(A,B,C,D) tools::win_emul::WaitForMultipleObjects(A,B,C,D)
        #       define SetEvent(A) tools::win_emul::SetEvent(A)
        #       define ResetEvent(A) tools::win_emul::ResetEvent(A)
        #       define PulseEvent(A) tools::win_emul::PulseEvent(A)
        #       define CreateEventW(A,B,C,D) tools::win_emul::CreateEventW(A,B,C,D)
        #       define OpenEventW(A,B,C) tools::win_emul::OpenEventW(A,B,C)
        #       define CloseHandle(A) tools::win_emul::CloseHandle(A)
        #       define GetTickCount() tools::win_emul::GetTickCount()
        #       define Sleep(A) tools::win_emul::Sleep(A)
        #       define fopen_s(A,B,C) tools::win_emul::fopen_s(A,B,C) 
        #       define _sopen_s(A,B,C,D,E) tools::win_emul::_sopen_s(A,B,C,D,E)
        #       define _strlwr_s(A,B) tools::win_emul::_strlwr_s(A,B) 
        #       define _strupr_s(A,B) tools::win_emul::_strupr_s(A,B) 
        #       define freopen_s(A,B,C,D) tools::win_emul::freopen_s(A,B,C,D) 
        #       define strcpy_s(A,B,C) tools::win_emul::strcpy_s(A,B,C) 
        #       define strncpy_s(A,B,C,D) tools::win_emul::strncpy_s(A,B,C,D) 
        #       define strcat_s(A,B,C) tools::win_emul::strcat_s(A,B,C) 

        #       include <stdint.h>
        #       include <errno.h>
        #       include <cstdio>
        #       define GetLastError() errno

        #       include <limits.h>
        #       include <stdlib.h>
        #       define GetFullPathName(A,B,C,D) realpath(A,C)

        #       include <cctype>
        #       include <algorithm>
        #       define CharUpperBuff(A,B) { std::string __str(A,B); std::transform(__str.begin(),__str.end(),__str.begin(),::toupper); strcpy(A,__str.c_str()); }

inline BOOL SetEnvironmentVariable(LPCTSTR lpName, LPCTSTR lpValue)
{
    return setenv(lpName, lpValue, 1);
}

        /* _countof helper */
        #if !defined(_countof)
            #if !defined(__cplusplus)
                #define _countof(_Array) (sizeof(_Array) / sizeof(_Array[0]))
            #else
extern "C++"
{
template <typename _CountofType, size_t _SizeOfArray>
char (*__countof_helper(_CountofType (&_Array)[_SizeOfArray]))[_SizeOfArray];
                #define _countof(_Array) sizeof(*__countof_helper(_Array))
}
            #endif
        #endif

    #endif
#endif

