# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage

from spack.package import *


class RrtmgpCpp(CMakePackage):
    """E3SM's C++/Kokkos implementation of RTE+RRTMGP, including gas and
    cloud optics, coefficient readers, and broadband/by-band flux solvers."""

    homepage = "https://github.com/E3SM-Project/rte-rrtmgp"
    url = "https://github.com/E3SM-Project/rte-rrtmgp/archive/71693e7490db0908a625eadb6ac3f23967de2c7d.tar.gz"
    maintainers("larenspear")
    license("BSD-3-Clause")
    version(
        "erf-26.11",
        url=url,
        sha256="a45c2ccdadedc71bdcf9db9e908e84bfd26b0febe8c041c695ac5ce8ca31184d",
    )
    variant("shared", default=True, description="Build a shared library")
    variant("openmp", default=False, description="Enable the Kokkos OpenMP backend")
    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("cmake@3.24:", type=("build", "test"))
    depends_on("gmake", type=("build", "test"))
    depends_on("kokkos@5.1.0+legacy_view+serial~cuda~rocm~sycl cxxstd=20")
    depends_on("kokkos+openmp", when="+openmp")
    depends_on("kokkos~openmp", when="~openmp")
    depends_on("netcdf-c+shared")
    depends_on("rrtmgp-data@erf-26.11", type=("build", "run"))

    # Preserve all build inputs in Spack hashes and installed provenance.
    patch("standalone-install.patch")

    root_cmakelists_dir = "spack-build-interface"
    test_requires_compiler = True

    def cmake_args(self):
        return [
            self.define_from_variant("BUILD_SHARED_LIBS", "shared"),
            self.define("CMAKE_CXX_STANDARD", 20),
            self.define("Kokkos_ROOT", self.spec["kokkos"].prefix),
            self.define("RRTMGP_NETCDF_INCLUDE_DIR", self.spec["netcdf-c"].prefix.include),
            self.define("RRTMGP_NETCDF_LIBRARY", self.spec["netcdf-c"].libs),
            self.define("RRTMGP_DATA_DIR", self.spec["rrtmgp-data"].prefix.share.rrtmgp),
        ]

    @run_after("install")
    @on_package_attributes(run_tests=True)
    def check_install(self):
        self._check_consumer(join_path(self.package_dir, "test"))

    def test_consumer(self):
        """Run the upstream one-column shortwave and longwave reference cases."""
        self._check_consumer(self.test_suite.current_test_data_dir)

    def _check_consumer(self, source):
        cmake = Executable(self.spec["cmake"].prefix.bin.cmake)
        with working_dir("installed-consumer", create=True):
            cmake(
                "-S",
                source,
                "-B",
                ".",
                "-G",
                "Unix Makefiles",
                self.define("CMAKE_MAKE_PROGRAM", self.spec["gmake"].prefix.bin.make),
                self.define("CMAKE_PREFIX_PATH", self.prefix),
            )
            cmake("--build", ".", "--parallel", "2")
            Executable(self.spec["cmake"].prefix.bin.ctest)("--output-on-failure")
