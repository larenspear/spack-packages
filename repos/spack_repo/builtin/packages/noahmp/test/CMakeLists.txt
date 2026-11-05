cmake_minimum_required(VERSION 3.17)
project(NoahMPConsumer LANGUAGES CXX Fortran)

find_package(NoahMP ${NOAHMP_VERSION} EXACT CONFIG REQUIRED)
enable_testing()

add_executable(physics physics.f90)
target_link_libraries(physics PRIVATE NoahMP::noahmp)
add_test(NAME physics COMMAND physics)

add_executable(coupling coupling.cpp binding.F90)
target_link_libraries(coupling PRIVATE NoahMP::noahmp)
if(NOAHMP_VERSION VERSION_LESS 5.1.1)
    target_compile_definitions(coupling PRIVATE NOAHMP_OLD_INTERFACE)
endif()
add_test(NAME coupling COMMAND coupling)

add_executable(data data.f90)
target_include_directories(data PRIVATE ${NETCDF_FORTRAN_INCLUDE_DIR})
target_link_libraries(data PRIVATE NoahMP::noahmp ${NETCDF_FORTRAN_LIBRARY})
add_test(NAME data COMMAND data "${NoahMP_DATA_DIR}")
