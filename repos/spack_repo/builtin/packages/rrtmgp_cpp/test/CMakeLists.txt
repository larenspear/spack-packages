cmake_minimum_required(VERSION 3.24)
project(RrtmgpConsumer LANGUAGES CXX)
find_package(Rrtmgp 26.11 EXACT CONFIG REQUIRED)
add_executable(allsky "${RRTMGP_EXAMPLE_DIR}/rrtmgp_allsky.cpp")
target_link_libraries(allsky PRIVATE Rrtmgp::rrtmgp)
enable_testing()
foreach(band IN ITEMS sw lw)
  if(band STREQUAL "sw")
    set(points 224)
  else()
    set(points 256)
  endif()
  add_test(NAME allsky-${band} COMMAND allsky
    "${RRTMGP_DATA_DIR}/rrtmgp-allsky.nc"
    "${RRTMGP_DATA_DIR}/rrtmgp-data-${band}-g${points}-2018-12-04.nc"
    "${RRTMGP_DATA_DIR}/rrtmgp-cloud-optics-coeffs-${band}.nc" 1 1)
  # Upstream checks reference flux sums and broadband/by-band consistency at
  # relative tolerance 1e-10. Also reject NaNs/Infs, which evade those comparisons.
  set_tests_properties(allsky-${band} PROPERTIES TIMEOUT 120
    FAIL_REGULAR_EXPRESSION "(^|[ =])[-+]?(nan|inf)([^a-zA-Z]|$)")
endforeach()
