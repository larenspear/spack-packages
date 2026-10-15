import os

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage

from spack.package import *


class Erf(CMakePackage, CudaPackage):
    """ERF solves the compressible Navier-Stokes on a Arakawa C-grid
    for large-scale weather modeling.
    """

    homepage = "https://erf.readthedocs.io/en/latest/index.html"
    url = "https://github.com/erf-model/ERF/archive/refs/tags/25.10.tar.gz"
    git = "https://github.com/erf-model/ERF.git"

    def url_for_version(self, version):
        return f"https://github.com/erf-model/ERF/archive/refs/tags/{version}.tar.gz"

    test_requires_compiler = True

    maintainers("larenspear")

    license("BSD-3-Clause", checked_by="larenspear")

    # Each ERF release vendors a same-numbered AMReX submodule (ERF YY.MM tracks
    # AMReX YY.MM) and follows AMReX's fast-moving API, which offers no
    # cross-release compatibility guarantee: e.g. ERF 25.12 uses amrex::*::Build
    # overloads missing from amrex@25.02 and the ArrayND ncomp() accessor removed
    # by amrex@26.04. Declare each release together with its matching AMReX pin
    # so a new version cannot be added without one. The development branch
    # tracks AMReX's development branch the same way.
    version("develop", branch="development")
    depends_on("amrex@develop", when="@develop", type=("build", "link"))

    for _v, _sha in (
        ("26.09", "d86372f6b9d85996f1b30beb7353c01b33f1bf0e454c0e63c913b255e17dadc0"),
        ("26.06", "379ffdebb30242cacddde95357511d5de1da29332c6624d5470088927743db78"),
        ("26.05", "198f8093b7afb2e405f509beca3b6a6da94c299af564e889e3c80daecc376e65"),
        ("26.04", "93a7ef8e6b55c4f830fac85129d6cf36c0b0e931eb060d7f8a1579afea8f909d"),
        ("26.03", "90399f4a7904e2b0d3c8e785484bebb89f2a5c46826fa4d751f939c0678d2d47"),
        ("26.02", "22b6570b9f022e58e0952801a85d4634b3076b40953422e0bd4df3de1d22e44d"),
        ("26.01", "1b40ec52b225e6bed1455f074cec04db1337121683ae1300c3adb3d048596d4d"),
        ("25.12", "0d11389c59561dea51f6b12253e1af7ab157599e0657bde603db7c102713e158"),
        ("25.11", "bd4160686eb52a49173ba07fe68ef86c2cd20b17283eaacf01b6c2d61a82982f"),
        ("25.10", "92575d25a8e87266f1b3a9a0c16a5755b84c45d489a060abeec6ddea8b8d8fe0"),
        ("25.08", "c8723384e00fb4bbb694385bdbc5187f38ee1509a0a18a23efc1094212fd21f4"),
        ("25.07", "bee8c136872c4e5400fdf2f6a432c8dc17f9b8384715158d9780a2c561a51642"),
        ("25.06", "dd1d627faf67477e3fa1f58b006f7e2b00316c66e8c99baf8b6cfbedce37b5f2"),
        ("25.05", "eb56a44d915d6af3ad30438dff6b96d9c489ae7c610fe4cdd0c17f2f26cc4b28"),
        ("25.04", "fc6837b252c1cebd0f2d38cdb3cea8ad55c837e4163c76e5d3508d973b282a42"),
        ("25.03", "3068c0c5f66538bcc1a12ee8c3eb142e5d02b73b71ab1cfbb244a053e8d5cf4a"),
        ("25.01", "11e48aadfc420c3f9adb05a0c5778776d6cb0915476532fd7a095d9f167ef584"),
        ("24.11", "19e7ce4829a46c98baf55b1dc4b2cefc508f2db41182e47c0ca788fe9280783f"),
        ("24.10", "7c9ba35374e71103fab8c5ba3ea107b4574e3270038bc3e8cbdcbe30eba26e7a"),
    ):
        version(_v, sha256=_sha)
        depends_on(f"amrex@{_v}", when=f"@{_v}", type=("build", "link"))

    # Releases before 24.10 predate ERF's strict find_package(AMReX COMPONENTS)
    # integration and keep their historical unpinned AMReX dependency.
    for _v, _sha in (
        ("24.09", "08326c03a28e20e7b173ac09c88eb547d01fe4f6a6f7de126c042791587d8ca5"),
        ("24.08", "7598da84a55f92f7cb8efac813e0c403f694e439fa4048170c762e3cad06fc82"),
        ("24.06", "f55c9c006de97fe299e10fe599682a3812ad009280a041e6ff56836ca4f1cd61"),
        ("24.05", "a3d39c4ea80d242885e80cbb9b6c6aa919fd467a3b56ef455443b4c062e6e5ea"),
        ("24.04", "824d9664717bf6f505eb72b5206deb13ca76908176c27d2c8ca55d21ae4a1bf7"),
        ("24.03", "351dca62d3dddfff613010f5fcbfc3a915e9146606716b4c8326ebfafdd05f10"),
        ("24.02", "0156f92857110e692cf1debf8f2e9991dce13f54a07140e107c1fecf77685ebc"),
        ("24.01", "f4deab84731602b11682101ca76a6ddb5ece4d897e53512155ad264cf8f9fddc"),
        ("23.12", "f168a2c9b30cb104b8e7646bf10c18c91520b875acda688a9c3659906e276ac3"),
        ("23.11", "ee0566d69d4e75e423e9ca4b00eb04f8fde45484d390e737a22df1532a12a7de"),
        ("23.10", "ca0035853721fa0dd0da52293a155f0a85615950a8a269599114c30fc608fe39"),
    ):
        version(_v, sha256=_sha)

    variant("mpi", default=False, description="Enable MPI support")
    variant("openmp", default=False, description="Enable OpenMP support")
    variant("netcdf", default=False, description="Enable NetCDF support")
    variant("particles", default=False, description="Enable particle support")
    variant("multiblock", default=False, description="Enable multiblock support")
    variant("tests", default=False, description="Enable tests")
    variant("fcompare", default=False, description="Enable fcompare")
    variant("fft", default=False, description="Enable FFT support")
    variant(
        "noahmp",
        default=False,
        description="Enable the Noah-MP land surface model",
        when="@25.12:",
    )

    with default_args(type="build"):
        depends_on("cmake@3.20:")
        depends_on("git")
        depends_on("c")
        depends_on("cxx")
        depends_on("fortran")
        depends_on("pkgconfig")
        # The Noah-MP ERF driver generates part of its interface with Python (26.09+).
        depends_on("python@3:", when="+noahmp")

    with default_args(type=("build", "link")):
        for v in ("mpi", "openmp", "cuda"):
            depends_on(f"amrex+{v}", when=f"+{v}")
            depends_on(f"amrex~{v}", when=f"~{v}")
        for sm in CudaPackage.cuda_arch_values:
            depends_on(f"amrex+cuda cuda_arch={sm}", when=f"+cuda cuda_arch={sm}")

        # ERF 24.10+ CMake unconditionally requests the AMReX PIC, PARTICLES, and
        # LSOLVERS components via find_package(AMReX ... COMPONENTS), regardless of
        # ERF's own +particles variant, so AMReX must always provide them. Earlier
        # releases only needed AMReX particles when ERF's +particles was set.
        depends_on("amrex+pic+particles+linear_solvers", when="@24.10:")
        depends_on("amrex+particles", when="@:24.09+particles")
        depends_on("amrex~particles", when="@:24.09~particles")

        # The same find_package() call pins the AMReX precision components:
        # "PDOUBLE" "DOUBLE" is hard-coded through 26.05, and 26.06 derives it
        # from ERF_PRECISION, which defaults to DOUBLE. A single-precision AMReX
        # therefore fails component detection rather than building in single.
        depends_on("amrex precision=double", when="@24.10:")

        # Every ERF regression test pipes its plotfile through AMReX's fcompare,
        # and ERF 24.10+ looks for it at <amrex prefix>/bin/amrex_fcompare, which
        # an installed AMReX only ships with +plotfile_tools.
        depends_on("amrex+plotfile_tools", when="+tests")
        depends_on("amrex+plotfile_tools", when="+fcompare")

        # ERF 26.06 added gtest-based unit tests, which ERF enables by default
        # alongside the regression tests. Supply GoogleTest from Spack rather
        # than the bundled Submodules/googletest checkout (see patch()).
        depends_on("googletest", when="@26.06:+tests")

        depends_on("mpi", when="+mpi")
        depends_on("cuda@11.0:", when="+cuda")
        depends_on("fftw", when="+fft")

        with when("+netcdf"):
            depends_on("amrex+mpi")
            depends_on("netcdf-c+mpi+parallel-netcdf")
            depends_on("netcdf-fortran")
            depends_on("hdf5+mpi", when="+mpi")
        # The Noah-MP ERF driver (built in-tree, see the resources below) is Fortran
        # and reads NetCDF through the Fortran interface.
        depends_on("netcdf-fortran", when="+noahmp")

    conflicts("+openmp", when="+cuda", msg="Cannot enable both OpenMP and CUDA")
    conflicts("+fft", when="~mpi", msg="FFT support requires MPI")
    conflicts("+noahmp", when="~netcdf", msg="Noah-MP requires NetCDF")

    # AMReX releases through 26.07 omit AMReX_TracerParticle_mod_K.H from the
    # CMake install list even though AMReX's own AMReX_TracerParticles.cpp
    # includes it (superbuilds never notice because the whole Src/Particle
    # source dir is on the include path via BUILD_INTERFACE), so ERF's particle
    # code cannot compile against an installed AMReX. Fetch the header straight
    # from the pinned AMReX tag and stage it next to the ERF sources that
    # include it (see patch()). The header's content changed at AMReX 25.10 and
    # again at 26.04, hence one resource per band. Fixed upstream in AMReX PR
    # #5542 (amrex@26.08 and newer install the header); once the amrex recipe
    # backports that one-line patch to 24.10:26.07, these resources can go.
    _amrex_raw = "https://raw.githubusercontent.com/AMReX-Codes/amrex"
    for _lo, _hi, _sha in (
        ("24.10", "25.08", "d506f51a03889bda57c3f3a8c673be5f877f5d4af3ba28ab8b1018430b3ee8b5"),
        ("25.10", "26.03", "0999a126bc4fc26286b45a1ca98f13c4f34d06e4c816b42f83d8646af3983dcf"),
        ("26.04", "26.06", "eb42b0564473c5313fbc2ee2c802322d38143e1c8d1d2a59c85e21def442ec35"),
    ):
        resource(
            name="amrex-tracerparticle-header",
            url=f"{_amrex_raw}/{_lo}/Src/Particle/AMReX_TracerParticle_mod_K.H",
            sha256=_sha,
            expand=False,
            placement="amrex-tracerparticle-header",
            when=f"@{_lo}:{_hi}+particles",
        )

    # Noah-MP's ERF coupling layer (drivers/erf) is versioned with ERF, not with
    # Noah-MP's own releases: ERF's pin is 97 commits past the last Noah-MP tag
    # and moves with most ERF releases, and ERF compiles the driver in-tree with
    # its own precision macro (DOUBLE_PREC selects the Fortran real kind). So ERF
    # builds Noah-MP from the commit each release pins, fetched as a resource
    # now that the releases are tarballs. Pins from `git ls-tree <ref>
    # Submodules/Noah-MP`. The resource lands in a staging directory and patch()
    # moves it into place: release tarballs and git checkouts both carry an
    # empty placeholder directory at each submodule path, and Spack leaves a
    # resource alone when its destination already exists.
    _noahmp_pins = (
        ("25.12:26.04", "6dc16027de56f2abc9fe430016acd086625e9ae2"),
        ("26.05", "c08dd406761330ac823a3e268bd2e98eb6889b40"),
        ("26.06", "41587582bf9b73786ce693660b0a56ff412d1eff"),
        ("26.09", "e03243d2c5eac19b1c6a02a2c3ca12f03f92cceb"),
        ("develop", "de71219fc79a84aa3c223a41e96630f89982937b"),
    )
    for _versions, _commit in _noahmp_pins:
        resource(
            name="noahmp",
            git="https://github.com/erf-model/noahmp.git",
            commit=_commit,
            destination="spack-resources",
            placement="noahmp",
            when=f"@{_versions}+noahmp",
        )

    @staticmethod
    def _move_into_place(src, dst):
        """Move a staged resource onto the submodule path ERF's CMake expects."""
        # An uninitialised submodule leaves an empty directory behind.
        if os.path.isdir(dst) and not os.listdir(dst):
            os.rmdir(dst)
        if os.path.exists(dst):
            raise InstallError(f"{dst} is already populated; refusing to replace it")
        mkdirp(os.path.dirname(dst))
        os.rename(src, dst)

    def patch(self):
        if self.spec.satisfies("+noahmp"):
            self._move_into_place(join_path("spack-resources", "noahmp"), "Submodules/Noah-MP")

        # ERF 26.06+ unit tests add_subdirectory() the bundled googletest
        # checkout, which is not fetched. Redirect them to the Spack-provided
        # GoogleTest: both test
        # executables already link GTest::gtest, the target name that
        # find_package(GTest) defines, and Tests/Unit already include(GoogleTest)
        # for gtest_discover_tests.
        if self.spec.satisfies("@26.06:+tests"):
            unit_cmakelists = join_path("Tests", "Unit", "CMakeLists.txt")
            marker = (
                "add_subdirectory(${PROJECT_SOURCE_DIR}/Submodules/googletest\n"
                "                 ${PROJECT_BINARY_DIR}/Submodules/googletest\n"
                "                 EXCLUDE_FROM_ALL)"
            )
            with open(unit_cmakelists, encoding="utf-8") as f:
                contents = f.read()
            if marker not in contents:
                raise InstallError("ERF unit tests no longer match the googletest patch marker")
            with open(unit_cmakelists, "w", encoding="utf-8") as f:
                f.write(contents.replace(marker, "find_package(GTest REQUIRED)"))

        # Place the AMReX header fetched by the resource above into
        # Source/Particles, which ERF's particle build already puts on its
        # include path (as -I, searched before AMReX's -isystem headers), so
        # the copy stays harmless once AMReX installs the header itself.
        # Keep this range in sync with the resource bands above.
        if self.spec.satisfies("@24.10:26.06+particles"):
            copy(
                join_path("amrex-tracerparticle-header", "AMReX_TracerParticle_mod_K.H"),
                join_path("Source", "Particles"),
            )

    def cmake_args(self):
        args = [
            self.define_from_variant("ERF_ENABLE_MPI", "mpi"),
            self.define_from_variant("ERF_ENABLE_OPENMP", "openmp"),
            self.define_from_variant("ERF_ENABLE_NETCDF", "netcdf"),
            self.define_from_variant("ERF_ENABLE_PARTICLES", "particles"),
            self.define_from_variant("ERF_ENABLE_MULTIBLOCK", "multiblock"),
            # ERF spells these ERF_ENABLE_*; the ERF_BUILD_* names used here
            # before appear nowhere in ERF's CMake (checked at every tag back to
            # 23.10), so +tests configured no tests and +fcompare did nothing.
            self.define_from_variant("ERF_ENABLE_TESTS", "tests"),
            self.define_from_variant("ERF_ENABLE_FCOMPARE", "fcompare"),
            self.define_from_variant("ERF_ENABLE_FFT", "fft"),
            self.define_from_variant("ERF_ENABLE_NOAHMP", "noahmp"),
            self.define("ERF_DIM", "3"),
            self.define("ERF_USE_INTERNAL_AMREX", False),
        ]

        # ERF 26.06 keys its gtest unit tests off a separate option that
        # defaults to ON whenever the regression tests are on; state it
        # explicitly so ~tests never drags in a GoogleTest build.
        if self.spec.satisfies("@26.06:"):
            args.append(self.define_from_variant("ERF_ENABLE_UNIT_TESTS", "tests"))

        # Only ERF's test harness reads MPIEXEC_PREFLAGS, and --oversubscribe is
        # an Open MPI spelling that other MPI launchers reject.
        if self.spec.satisfies("+tests+mpi ^[virtuals=mpi] openmpi"):
            args.append(self.define("MPIEXEC_PREFLAGS", "--oversubscribe"))

        if self.spec.satisfies("+netcdf"):
            # ERF's CMake prepends NETCDF_DIR to CMAKE_PREFIX_PATH before its
            # FindNetCDF (nc-config / pkg-config); NetCDF_C_PATH and
            # NetCDF_FORTRAN_PATH, passed before, are read nowhere in ERF.
            args.append(self.define("NETCDF_DIR", self.spec["netcdf-c"].prefix))

        # The Noah-MP driver's FindNetCDF looks for the Fortran interface under the
        # C library's prefix only; Spack keeps netcdf-fortran apart, so hand it the
        # answers it would search for.
        if self.spec.satisfies("+noahmp"):
            netcdf_fortran = self.spec["netcdf-fortran"]
            args.extend(
                [
                    self.define("NETCDF_INCLUDES_F90", netcdf_fortran.prefix.include),
                    self.define("NETCDF_LIBRARIES_F90", netcdf_fortran.libs.joined(";")),
                ]
            )

        if "+cuda" in self.spec:
            archs = self.spec.variants["cuda_arch"].value or ["80"]
            args.append(self.define("CMAKE_CUDA_ARCHITECTURES", ";".join(archs)))
            args.extend(
                [
                    self.define("ERF_ENABLE_CUDA", "ON"),
                    self.define("CUDAToolkit_ROOT", self.spec["cuda"].prefix),
                ]
            )

        return args

    def setup_build_environment(self, env):
        super().setup_build_environment(env)
        env.set("AMREX_HOME", self.spec["amrex"].prefix)
        if "+openmp" in self.spec:
            if "%clang" in self.spec or "%gcc" in self.spec:
                env.append_flags("CFLAGS", self.compiler.openmp_flag)
                env.append_flags("CXXFLAGS", self.compiler.openmp_flag)
                env.append_flags("FFLAGS", self.compiler.openmp_flag)
