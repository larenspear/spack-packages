# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage

from spack.package import *


class EamxxShoc(CMakePackage):
    """EAMxx SHOC turbulence kernels and shared saturation physics as an
    independent library. This is the double-precision, pack-size-one interface
    used by ERF, without EAMxx's atmosphere-process driver."""

    homepage = "https://github.com/E3SM-Project/E3SM"
    git = "https://github.com/E3SM-Project/E3SM.git"
    maintainers("larenspear")
    license("BSD-3-Clause")
    version(
        "erf-26.11",
        commit="2eb52d9b3d452e593f3825f9408507cae3519bf6",
        git_sparse_paths=["components/eamxx/src/physics", "components/eamxx/src/share"],
    )
    variant("shared", default=True, description="Build a shared library")
    variant("mpi", default=True, description="Use EKAT's MPI communication interface")
    variant("openmp", default=False, description="Use the Kokkos OpenMP backend")

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("cmake@3.24:", type=("build", "test"))
    depends_on("gmake", type=("build", "test"))
    depends_on("ekat@2.1.0.erf2611")
    depends_on("ekat+mpi", when="+mpi")
    depends_on("ekat~mpi", when="~mpi")
    depends_on("ekat+openmp", when="+openmp")
    depends_on("ekat~openmp", when="~openmp")
    depends_on("kokkos@5.1.0+legacy_view cxxstd=20")

    # Kokkos 5 hides the deprecated MemoryManaged alias; MemoryTraits<> is
    # exactly its underlying managed-view type.
    patch("kokkos-memory-traits.patch")

    # Preserve all build inputs in Spack hashes and installed provenance.
    patch("standalone-install.patch")

    root_cmakelists_dir = "spack-build-interface"
    test_requires_compiler = True

    def cmake_args(self):
        return [
            self.define_from_variant("BUILD_SHARED_LIBS", "shared"),
            self.define("Ekat_ROOT", self.spec["ekat"].prefix),
        ]

    @run_after("install")
    @on_package_attributes(run_tests=True)
    def check_install(self):
        self._check_consumer(join_path(self.package_dir, "test"))

    def test_consumer(self):
        """Exercise an installed SHOC dispatch kernel and its exported ABI."""
        self._check_consumer(self.test_suite.current_test_data_dir)

    def _check_consumer(self, source):
        cmake = Executable(self.spec["cmake"].prefix.bin.cmake)
        mpi_args = []
        if "+mpi" in self.spec:
            mpi_args = [
                self.define("MPI_C_COMPILER", self.spec["mpi"].mpicc),
                self.define("MPI_CXX_COMPILER", self.spec["mpi"].mpicxx),
            ]
        with working_dir("installed-consumer", create=True):
            cmake(
                "-S",
                source,
                "-B",
                ".",
                "-G",
                "Unix Makefiles",
                self.define("CMAKE_MAKE_PROGRAM", self.spec["gmake"].prefix.bin.make),
                self.define(
                    "CMAKE_PREFIX_PATH",
                    [str(s.prefix) for s in self.spec.traverse(deptype="link")],
                ),
                *mpi_args,
            )
            cmake("--build", ".", "--parallel", "2")
            Executable(self.spec["cmake"].prefix.bin.ctest)("--output-on-failure")
