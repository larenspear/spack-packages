cmake_minimum_required(VERSION 3.24)
project(EamxxShoc VERSION 26.11 LANGUAGES C CXX)
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
find_package(Ekat 2.1 CONFIG REQUIRED COMPONENTS Core KokkosUtils Pack Algorithm)
get_filename_component(source "${CMAKE_CURRENT_SOURCE_DIR}/../components/eamxx/src" ABSOLUTE)
include(sources.cmake)
list(TRANSFORM shoc_sources PREPEND "${source}/")
add_library(eamxx_shoc ${shoc_sources})
add_library(EamxxShoc::shoc ALIAS eamxx_shoc)
set_target_properties(eamxx_shoc PROPERTIES EXPORT_NAME shoc POSITION_INDEPENDENT_CODE ON)
target_compile_features(eamxx_shoc PUBLIC cxx_std_20)
target_compile_definitions(eamxx_shoc PUBLIC SCREAM_SHOC_SMALL_KERNELS)
target_link_libraries(eamxx_shoc PUBLIC ekat::AllLibs)
target_include_directories(eamxx_shoc PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
  $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}/eamxx-shoc>)
foreach(dir IN ITEMS . physics/share physics/shoc physics/shoc/impl)
  target_include_directories(eamxx_shoc PUBLIC
    $<BUILD_INTERFACE:${source}/${dir}>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}/eamxx-shoc/${dir}>)
endforeach()
install(FILES eamxx_config.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/eamxx-shoc)
# Install the complete kernel header closure, excluding EAMxx's process driver.
include(headers.cmake)
foreach(header IN LISTS shoc_headers)
  get_filename_component(dir "${header}" DIRECTORY)
  install(FILES "${source}/${header}" DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/eamxx-shoc/${dir}")
endforeach()
install(TARGETS eamxx_shoc EXPORT EamxxShocTargets
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR} LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
install(EXPORT EamxxShocTargets NAMESPACE EamxxShoc:: DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/EamxxShoc)
configure_package_config_file(EamxxShocConfig.cmake.in EamxxShocConfig.cmake
  INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/EamxxShoc)
write_basic_package_version_file(EamxxShocConfigVersion.cmake VERSION 26.11 COMPATIBILITY ExactVersion)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/EamxxShocConfig.cmake
              ${CMAKE_CURRENT_BINARY_DIR}/EamxxShocConfigVersion.cmake
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/EamxxShoc)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/../LICENSE DESTINATION ${CMAKE_INSTALL_DATADIR}/eamxx-shoc)
