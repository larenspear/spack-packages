# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage

from spack.package import *


class Ww3(CMakePackage):
    """WAVEWATCH III's ERF coupling fork, using the ST6/PR1/MPI switch set
    documented for ERF's ww3_ts3 case. The fork's ww3_shel expects a second
    MPMD program; this package does not claim standalone coupled execution."""

    homepage = "https://github.com/erf-model/WW3"
    url = (
        "https://github.com/erf-model/WW3/archive/f5fa5822849e33976cdc935a91b304c60bc2a976.tar.gz"
    )
    maintainers("larenspear")
    license("LGPL-3.0-only")
    version(
        "erf-26.11",
        url=url,
        sha256="878351c4409d2e5cd7273b7fde0a4dbfe2aec7e92a8c6b487b3d939b202aebaf",
    )
    variant("netcdf", default=True, description="Build NetCDF input/output programs")
    depends_on("c", type="build")
    depends_on("fortran", type="build")
    depends_on("cmake@3.19:", type=("build", "test"))
    depends_on("gmake", type=("build", "test"))
    depends_on("mpi")
    depends_on("netcdf-c", when="+netcdf")
    depends_on("netcdf-fortran", when="+netcdf")
    patch("installed-config.patch")
    patch("nl1-format.patch")
    patch("point-io-nl1-init.patch")
    test_requires_compiler = True

    def cmake_args(self):
        args = [
            self.define(
                "SWITCH",
                join_path(self.stage.source_path, "regtests/ww3_ts3/input/switch_ST6_PR1_MPI"),
            ),
            self.define_from_variant("NETCDF", "netcdf"),
            self.define("ENDIAN", "BIG"),
            # Run the I/O case against the installed library, with a generated grid.
            self.define("BUILD_TESTING", False),
            self.define("MPI_Fortran_COMPILER", self.spec["mpi"].mpifc),
        ]
        if "+netcdf" in self.spec:
            args.extend(
                [
                    self.define(
                        "NetCDF_C_INCLUDE_FILE",
                        join_path(self.spec["netcdf-c"].prefix.include, "netcdf.h"),
                    ),
                    self.define("NetCDF_C_LIBRARY", self.spec["netcdf-c"].libs),
                    self.define(
                        "NetCDF_C_CONFIG_EXECUTABLE",
                        join_path(self.spec["netcdf-c"].prefix.bin, "nc-config"),
                    ),
                    self.define(
                        "NetCDF_Fortran_INCLUDE_FILE",
                        join_path(self.spec["netcdf-fortran"].prefix.include, "netcdf.mod"),
                    ),
                    self.define("NetCDF_Fortran_LIBRARY", self.spec["netcdf-fortran"].libs),
                    self.define(
                        "NetCDF_Fortran_CONFIG_EXECUTABLE",
                        join_path(self.spec["netcdf-fortran"].prefix.bin, "nf-config"),
                    ),
                ]
            )
        return args

    @run_after("install")
    def install_examples(self):
        mkdirp(self.prefix.share.ww3)
        install("LICENSE.md", self.prefix.share.ww3)
        install_tree("regtests/ww3_ts3/input", join_path(self.prefix.share.ww3, "ww3_ts3"))
        install_tree("regtests/unittests", join_path(self.prefix.share.ww3, "tests"))

    @run_after("install")
    @on_package_attributes(run_tests=True)
    def check_install(self):
        self._check_consumer(join_path(self.package_dir, "test"))

    def test_consumer(self):
        """Generate a grid and verify binary point I/O using installed Fortran modules."""
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
                self.define(
                    "CMAKE_PREFIX_PATH",
                    [self.prefix] + [d.prefix for d in self.spec.dependencies(deptype="link")],
                ),
                self.define("WW3_PREFIX", self.prefix),
            )
            cmake("--build", ".", "--parallel", "2")
            Executable(self.spec["cmake"].prefix.bin.ctest)("--output-on-failure")
