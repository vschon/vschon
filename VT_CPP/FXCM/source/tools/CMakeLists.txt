cmake_minimum_required (VERSION 2.8.7) 
 
set (PROJECT tools) 
  
project (${PROJECT})

if(DEFINED Mac32)
  set(ARCHFLAGS "-arch i386 -DMac32")
elseif(${CMAKE_SYSTEM} MATCHES "Linux")
  if(${CMAKE_SYSTEM_PROCESSOR} MATCHES "i[3-6]86")
    set(ARCHFLAGS "-march=i486")
  endif()
  set(ARCHFLAGS "${ARCHFLAGS} -D_XOPEN_SOURCE=600")
else()
  set(ARCHFLAGS "")
endif()

set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${ARCHFLAGS}")
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${ARCHFLAGS}")

if (NOT LIBRARY_OUTPUT_PATH)
  set (LIBRARY_OUTPUT_PATH ${CMAKE_CURRENT_SOURCE_DIR}/lib)
endif ()

include_directories (
                     ${CMAKE_CURRENT_SOURCE_DIR}/win_emul
                     ${CMAKE_CURRENT_SOURCE_DIR}/date
                     ${CMAKE_CURRENT_SOURCE_DIR}/mutex
                     ${CMATE_CURRENT_SOURCE_DIR}/threading
                    )   


set (SOURCES 
    tools.cpp
    tools_stdafx.cpp
    date/date.cpp
    threading/PosixThreadImpl.cpp
    threading/ThreadHandle.cpp
    threading/PosixCondVarWrapper.cpp
    win_emul/CWinEventHandle.cpp
    mutex/Mutex.cpp
    win_emul/winevent.cpp
    win_emul/winCRTsecure.cpp
    ) 

if (${CMAKE_SYSTEM} MATCHES "Linux")
  if (CMAKE_COMPILER_IS_GNUCXX) 
    add_definitions (-fPIC)
  elseif (CMAKE_COMPILER_IS_GNUCC)
    add_definitions (-fPIC)
  endif()
endif()

# Uncomment next line to enable generating debugging symbols
# add_definitions (-g)

add_library (${PROJECT} SHARED ${HEADERS} ${SOURCES})  

if (${CMAKE_SYSTEM} MATCHES "Linux")
  target_link_libraries (${PROJECT} rt pthread)
elseif (${CMAKE_SYSTEM} MATCHES "Darwin")
  target_link_libraries (${PROJECT} pthread)
endif ()

if (${CMAKE_SYSTEM} MATCHES "Linux")
    set_target_properties (${PROJECT} PROPERTIES
          LINK_FLAGS -Wl,-rpath,.
    )
elseif (${CMAKE_SYSTEM} MATCHES "Darwin")
    set_target_properties (${PROJECT} PROPERTIES
          BUILD_WITH_INSTALL_RPATH 1
          INSTALL_NAME_DIR "."
    )
endif ()

