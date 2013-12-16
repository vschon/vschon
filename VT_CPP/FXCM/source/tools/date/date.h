#pragma once

#ifndef WIN32
#   ifndef DATE

typedef double DATE;

#   endif
#   ifndef SYSTEMTIME_DEFINED

typedef struct _SYSTEMTIME {
    WORD wYear;
    WORD wMonth;
    WORD wDayOfWeek;
    WORD wDay;
    WORD wHour;
    WORD wMinute;
    WORD wSecond;
    WORD wMilliseconds;
} SYSTEMTIME, *PSYSTEMTIME, *LPSYSTEMTIME;

#       define SYSTEMTIME_DEFINED
#   endif
#   ifndef WCHAR

typedef wchar_t WCHAR;

#   endif
#   ifndef TIME_ZONE_INFORMATION

typedef struct _TIME_ZONE_INFORMATION {
    long Bias;
    WCHAR StandardName[ 32 ];
    SYSTEMTIME StandardDate;
    long StandardBias;
    WCHAR DaylightName[ 32 ];
    SYSTEMTIME DaylightDate;
    long DaylightBias;
} TIME_ZONE_INFORMATION, *PTIME_ZONE_INFORMATION, *LPTIME_ZONE_INFORMATION;

#       define TIME_ZONE_ID_INVALID  ((DWORD)0xFFFFFFFF)
#       define TIME_ZONE_ID_UNKNOWN  ((DWORD)0)
#       define TIME_ZONE_ID_STANDARD ((DWORD)1)
#       define TIME_ZONE_ID_DAYLIGHT ((DWORD)2)
#   endif
#else
#   include <windows.h>
#   include <oleauto.h>
#endif

namespace tools
{
    namespace date
    {
        INT GSTOOLS3 OleTimeToWindowsTime(double dt, SYSTEMTIME *st);
        INT GSTOOLS3 WindowsTimeToOleTime(SYSTEMTIME *st, double *dt);
        INT GSTOOLS3 OleTimeToCTime(double dt, struct tm *t);
        INT GSTOOLS3 CTimeToOleTime(struct tm *t, double *dt);
        void GSTOOLS3 CTimeToWindowsTime(const struct tm *t, SYSTEMTIME *st);
        void GSTOOLS3 WindowsTimeToCTime(const SYSTEMTIME *st, struct tm *t);
        void GSTOOLS3 GetLocalWindowsTime(SYSTEMTIME *st);
        void GSTOOLS3 GetSystemWindowsTime(SYSTEMTIME *st);
        char GSTOOLS3 *DateStringToCTime(const char *s, const char *format, struct tm *tm);
        BOOL GSTOOLS3 TzSpecificLocalTimeToUTCTime(LPTIME_ZONE_INFORMATION lpTimeZoneInformation,
                                             LPSYSTEMTIME lpLocalTime,
                                             LPSYSTEMTIME lpUniversalTime);
        BOOL GSTOOLS3 UTCTimeToTzSpecificLocalTime(LPTIME_ZONE_INFORMATION lpTimeZoneInformation,
                                             LPSYSTEMTIME lpUniversalTime,
                                             LPSYSTEMTIME lpLocalTime);
        DWORD GSTOOLS3 GetTzInformation(LPTIME_ZONE_INFORMATION lpTimeZoneInformation, const char *szTimeZone = NULL);

        enum eTimeZone
        {
            Local,
            EST,
            UTC
        };

        DATE GSTOOLS3 DateConvertTz(DATE dt, eTimeZone tzFrom, eTimeZone tzTo);
        DATE GSTOOLS3 OneSecond();
        DATE GSTOOLS3 DateNow();
    }
}

#ifndef WIN32
#   define VariantTimeToSystemTime(A,B) tools::date::OleTimeToWindowsTime(A,B)
#   define SystemTimeToVariantTime(A,B) tools::date::WindowsTimeToOleTime(A,B)
#   define GetLocalTime(A) tools::date::GetLocalWindowsTime(A)
#   define GetSystemTime(A) tools::date::GetSystemWindowsTime(A)
#   define TzSpecificLocalTimeToSystemTime(A,B,C) tools::date::TzSpecificLocalTimeToUTCTime(A,B,C)
#   define SystemTimeToTzSpecificLocalTime(A,B,C) tools::date::UTCTimeToTzSpecificLocalTime(A,B,C)
#   define GetTimeZoneInformation(A) tools::date::GetTzInformation(A)
#else
#   define strptime(A,B,C) tools::date::DateStringToCTime(A,B,C)
#endif
#define VariantTimeToUnixTime(A,B) tools::date::OleTimeToCTime(A,B)
#define UnixTimeToVariantTime(A,B) tools::date::CTimeToOleTime(A,B)
#define UnixTimeToSystemTime(A,B) tools::date::CTimeToWindowsTime(A,B)
#define SystemTimeToUnixTime(A,B) tools::date::WindowsTimeToCTime(A,B)
