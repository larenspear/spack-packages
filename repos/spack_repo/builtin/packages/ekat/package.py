# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

from spack_repo.builtin.build_systems.cmake import CMakePackage

from spack.package import *


class Ekat(CMakePackage):
    """E3SM's Kokkos-based utility library, including packs, algorithms,
    communication, logging, YAML parsing, and downstream testing support."""

    homepage = "https://github.com/E3SM-Project/EKAT"
    url = "https://github.com/E3SM-Project/EKAT/archive/ae5e7f8227943a25c66b1a1822973ec665d224e4.tar.gz"
    maintainers("larenspear")
    license("BSL-1.0")

    # ERF 26.11's exact snapshot, whose source reports version 2.1.0.
    version(
        "2.1.0.erf2611",
        url=url,
        sha256="759dd0e83d6ec5f3d29ce712107514f19619b82d09437ef15dfa7926bfe3858b",
    )

    variant("shared", default=True, description="Build shared libraries")
    variant("mpi", default=True, description="Enable MPI communication")
    variant("fortran", default=True, description="Enable Fortran support and tests")
    variant("openmp", default=False, description="Enable the Kokkos OpenMP backend")

    conflicts(
        "+mpi", when="platform=darwin", msg="This EKAT snapshot rejects MPI on Apple platforms"
    )

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("fortran", type="build", when="+fortran")
    depends_on("cmake@3.24:", type=("build", "test"))
    depends_on("gmake", type=("build", "test"))
    # The installed test-launcher is a Python program used by downstream tests.
    depends_on("python@3:", type=("build", "run"))
    depends_on("mpi", when="+mpi")
    # First supported backend is CPU; GPU compiler/architecture propagation
    # will be added alongside a qualified GPU consumer.
    depends_on("kokkos@5.1.0+legacy_view+serial~cuda~rocm~sycl cxxstd=20")
    depends_on("kokkos+openmp", when="+openmp")
    depends_on("kokkos~openmp", when="~openmp")
    depends_on("spdlog@1.17.0 cxxstd=20")
    depends_on("fmt@12.1.0")
    depends_on("yaml-cpp@0.6.3.ekat")
    # CatchMain is always built and exported, even with EKAT_ENABLE_TESTS=OFF.
    depends_on("catch2@2.13.8.ekat")

    patch("external-install.patch")
    test_requires_compiler = True

    def _config_dir(self, dependency, filename):
        matches = find(self.spec[dependency].prefix, filename, recursive=True)
        if len(matches) != 1:
            raise InstallError("Expected one {0} in {1}".format(filename, dependency))
        return os.path.dirname(matches[0])

    def cmake_args(self):
        args = [
            self.define_from_variant("BUILD_SHARED_LIBS", "shared"),
            self.define_from_variant("EKAT_ENABLE_MPI", "mpi"),
            self.define_from_variant("EKAT_ENABLE_FORTRAN", "fortran"),
            self.define("CMAKE_CXX_STANDARD", 20),
            self.define("CMAKE_POSITION_INDEPENDENT_CODE", True),
            self.define("CMAKE_FIND_PACKAGE_TARGETS_GLOBAL", True),
            self.define("EKAT_ENABLE_ALL_PACKAGES", True),
            self.define("EKAT_ENABLE_TESTS", self.run_tests),
            self.define("EKAT_ALLOW_INTERNAL_TPLS", False),
            self.define("FETCHCONTENT_FULLY_DISCONNECTED", True),
            self.define("EKAT_TEST_MAX_RANKS", 2 if "+mpi" in self.spec else 1),
            self.define("EKAT_TEST_MAX_THREADS", 2 if "+openmp" in self.spec else 1),
            self.define("Kokkos_DIR", self._config_dir("kokkos", "KokkosConfig.cmake")),
            self.define("spdlog_DIR", self._config_dir("spdlog", "spdlogConfig.cmake")),
            self.define("Catch2_DIR", self._config_dir("catch2", "Catch2Config.cmake")),
            self.define("YAML_CPP_ROOT", self.spec["yaml-cpp"].prefix),
        ]
        if "+mpi" in self.spec:
            args.extend(
                [
                    self.define("MPI_C_COMPILER", self.spec["mpi"].mpicc),
                    self.define("MPI_CXX_COMPILER", self.spec["mpi"].mpicxx),
                    self.define("EKAT_MPIRUN_EXE", self.spec["mpi"].prefix.bin.mpiexec),
                    self.define("EKAT_MPI_NP_FLAG", "-n"),
                    self.define("EKAT_MPI_EXTRA_ARGS", ""),
                ]
            )
        return args

    @run_after("install")
    def install_license(self):
        mkdirp(self.prefix.share.ekat)
        install("LICENSE.txt", self.prefix.share.ekat)

    @run_after("install")
    @on_package_attributes(run_tests=True)
    def check_install(self):
        self._check_consumer(join_path(self.package_dir, "test"))

    def test_consumer(self):
        """Compile and run an independent consumer of the installed exports."""
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
