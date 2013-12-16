cmake_minimum_required(VERSION 2.8.7)

project(VT_exe)

add_subdirectory(login)

set(vt_source_files main.cpp)
add_executable(VT ${vt_source_files})

target_link_libraries(VT login)
