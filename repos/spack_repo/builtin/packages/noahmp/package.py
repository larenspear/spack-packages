# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage

from spack.package import *


class Noahmp(CMakePackage):
    """Noah-MP is a state-of-the-art community land surface model used in
    weather and climate models including WRF, MPAS, WRF-Hydro/NWM, NOAA/UFS,
    NASA/LIS, and ERF.

    Noah-MP ships source plus per-host driver/interface code rather than a
    standalone library; only the ERF driver provides an installable CMake
    build, so this package builds the Noah-MP library through its ERF coupling
    interface. Other hosts (WRF, LIS, HRLDAS) compile Noah-MP into their own
    build and do not consume this package."""

    homepage = "https://github.com/NCAR/noahmp"
    git = "https://github.com/NCAR/noahmp.git"
    url = "https://github.com/NCAR/noahmp/archive/refs/tags/v5.2.1.tar.gz"

    maintainers("larenspear")

    # Noah-MP ships under a custom UCAR license (see LICENSE.txt); there is no
    # matching SPDX identifier, so no license() directive is set.

    version("5.2.1", sha256="4c9d4c6ebb2ccf707317933d704fe6f6d764f56a72aff1a7b35164e4ec80b4ed")
    version("5.2.0", sha256="3930250a4459859fbeb5583939fa680d84567764b4272fdb65dcb2f8836439fb")
    version("5.1.1", sha256="d3a2a2429b3edb32366e2810e7bc401cc925e6112708407023eef970deaa6bd6")
    version("5.1.0", sha256="45e1dd87eeffb56125a397fe82106185d989104ea9c1172d907b318c4aca7493")

    # Noah-MP has no top-level build system: it is meant to be compiled inside a
    # host model. The drivers/erf tree is the only one that provides a
    # standalone, installable CMake project (added with install/export rules in
    # v5.1.0), so it is used as the build root here. The resulting library
    # bundles the shared physics (src/, utility/) with the ERF coupling layer.
    # Earlier releases (5.0.0 and the 3.x series) lack drivers/erf entirely and
    # cannot be built this way.
    root_cmakelists_dir = "drivers/erf"

    # The C++ coupling headers hard-code double*. A single-precision build of
    # the Fortran modules is ABI-incompatible even though it compiles.
    variant("shared", default=True, description="Build a shared library")

    patch("v5.1.0-mpi.patch", when="@5.1.0")
    patch("library-install.patch")
    patch("land-input-precision.patch")
    patch("v5.1-double-precision.patch", when="@:5.1.1")

    test_requires_compiler = True

    depends_on("cmake@3.17:", type=("build", "test"))
    depends_on("gmake", type=("build", "test"))

    with default_args(type="build"):
        depends_on("c")
        depends_on("cxx")
        depends_on("fortran")

    with default_args(type=("build", "link")):
        depends_on("mpi")
        # The ERF driver writes NetCDF-4 files collectively with MPI-IO.
        depends_on("netcdf-c+mpi")
        depends_on("netcdf-fortran")

    def cmake_args(self):
        netcdf_c = self.spec["netcdf-c"]
        netcdf_fortran = self.spec["netcdf-fortran"]
        return [
            self.define("NOAHMP_VERSION", self.version),
            self.define_from_variant("BUILD_SHARED_LIBS", "shared"),
            # Upstream FindNetCDF assumes a common C/Fortran prefix. Supply
            # both interfaces explicitly, including lib64/external installs.
            self.define("NETCDF_INCLUDES", netcdf_c.prefix.include),
            self.define("NETCDF_LIBRARIES_C", netcdf_c.libs),
            self.define("NETCDF_INCLUDES_F90", netcdf_fortran.prefix.include),
            self.define("NETCDF_LIBRARIES_F90", netcdf_fortran.libs),
            self.define("MPI_Fortran_COMPILER", self.spec["mpi"].mpifc),
        ]

    @property
    def libs(self):
        return find_libraries("libnoahmp", root=self.prefix.lib, shared="+shared" in self.spec)

    @run_after("install")
    @on_package_attributes(run_tests=True)
    def check_install(self):
        self._check_library(join_path(self.package_dir, "test"))

    def test_library(self):
        """Build and run installed C++/Fortran consumers, including runtime data I/O."""
        self._check_library(self.test_suite.current_test_data_dir)

    def _check_library(self, source):
        cmake = Executable(self.spec["cmake"].prefix.bin.cmake)
        with working_dir("consumer", create=True):
            cmake(
                "-S",
                source,
                "-B",
                ".",
                "-G",
                "Unix Makefiles",
                self.define("CMAKE_MAKE_PROGRAM", self.spec["gmake"].prefix.bin.make),
                self.define("CMAKE_PREFIX_PATH", [self.prefix, self.spec["mpi"].prefix]),
                self.define("NOAHMP_VERSION", self.version),
                self.define(
                    "NETCDF_FORTRAN_INCLUDE_DIR", self.spec["netcdf-fortran"].prefix.include
                ),
                self.define("NETCDF_FORTRAN_LIBRARY", self.spec["netcdf-fortran"].libs),
            )
            cmake("--build", ".")
            ctest = Executable(self.spec["cmake"].prefix.bin.ctest)
            ctest("--output-on-failure")
