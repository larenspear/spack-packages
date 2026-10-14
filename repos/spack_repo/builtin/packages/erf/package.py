from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack_repo.builtin.build_systems.rocm import ROCmPackage

import os

from spack.package import *


def submodules(package):
    # Noah-MP comes from the standalone `noahmp` package, so the bundled
    # Submodules/Noah-MP is never fetched. RRTMGP is built from ERF's submodule
    # (ERF's CMake add_subdirectory()s it; there is no find_package path). EKAT is
    # fetched in patch() instead of here: its own submodules (Kokkos, yaml-cpp,
    # spdlog) are declared with SSH URLs, which Spack's recursive init would
    # follow and fail on without a key.
    subs = []
    if package.spec.satisfies("+rrtmgp"):
        subs.append("Submodules/RRTMGP")
    return subs


class Erf(CMakePackage, CudaPackage, ROCmPackage):
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
    # so a new version cannot be added without one.
    # The development branch tracks AMReX's, so it pins amrex@develop the way
    # each release pins its same-numbered AMReX.
    version("develop", branch="development", submodules=submodules)
    depends_on("amrex@develop", when="@develop", type=("build", "link"))

    for _v in (
        "26.09",
        "26.06",
        "26.05",
        "26.04",
        "26.03",
        "26.02",
        "26.01",
        "25.12",
        "25.11",
        "25.10",
        "25.08",
        "25.07",
        "25.06",
        "25.05",
        "25.04",
        "25.03",
        "25.01",
        "24.11",
        "24.10",
    ):
        version(_v, tag=_v, submodules=submodules)
        depends_on(f"amrex@{_v}", when=f"@{_v}", type=("build", "link"))

    # Releases before 24.10 predate ERF's strict find_package(AMReX COMPONENTS)
    # integration and keep their historical unpinned AMReX dependency.
    for _v in (
        "24.09",
        "24.08",
        "24.06",
        "24.05",
        "24.04",
        "24.03",
        "24.02",
        "24.01",
        "23.12",
        "23.11",
        "23.10",
    ):
        version(_v, tag=_v, submodules=submodules)

    # AMReX releases through 26.07 omit AMReX_TracerParticle_mod_K.H from the
    # CMake install list even though AMReX's own AMReX_TracerParticles.cpp
    # includes it (superbuilds never notice because the whole Src/Particle
    # source dir is on the include path via BUILD_INTERFACE), so ERF's particle
    # code cannot compile against an installed AMReX. Fetch the header straight
    # from the pinned AMReX tag and stage it next to the ERF sources that
    # include it (see patch()). The header's content changed at AMReX 25.10 and
    # again at 26.04, hence one resource per band. Fixed upstream in AMReX PR
    # #5542: amrex@26.08 and newer install the header, so ERF releases pinned
    # to those need no resource (an ERF 26.07 would extend the last band).
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

    variant("mpi", default=True, description="Enable MPI support")
    variant("openmp", default=False, description="Enable OpenMP support")
    variant("netcdf", default=False, description="Enable NetCDF support")
    variant("particles", default=False, description="Enable particle support")
    variant("multiblock", default=False, description="Enable multiblock support")
    variant("tests", default=False, description="Enable tests")
    variant("fcompare", default=False, description="Enable fcompare")
    variant("fft", default=False, description="Enable FFT support")
    variant("noahmp", default=False, description="Enable Noah-MP")
    variant(
        "precision",
        default="double",
        values=("double", "single"),
        multi=False,
        description="Floating point precision of the mesh and particle data",
    )
    variant("hdf5", default=False, description="Enable AMReX HDF5 plotfile I/O")
    variant("sycl", default=False, description="Enable the SYCL GPU backend (needs %oneapi)")
    variant("rrtmgp", default=False, description="Enable RTE-RRTMGP radiation (builds EKAT and Kokkos)")
    variant("windfarm", default=False, description="Enable the wind farm parameterizations")
    variant("wsm6_fort", default=False, description="Enable the WSM6 Fortran microphysics bridge")
    variant("wdm6_fort", default=False, description="Enable the WDM6 Fortran microphysics bridge")
    variant("tools", default=False, description="Build the additional tools (needs NetCDF)")

    with default_args(type="build"):
        depends_on("cmake@3.20:")
        depends_on("git")
        depends_on("c")
        depends_on("cxx")
        depends_on("fortran")
        depends_on("pkgconfig")

    with default_args(type=("build", "link")):
        for v in ("mpi", "openmp", "cuda", "rocm", "sycl", "hdf5"):
            depends_on(f"amrex+{v}", when=f"+{v}")
            depends_on(f"amrex~{v}", when=f"~{v}")
        for sm in CudaPackage.cuda_arch_values:
            depends_on(f"amrex+cuda cuda_arch={sm}", when=f"+cuda cuda_arch={sm}")
        for tgt in ROCmPackage.amdgpu_targets:
            depends_on(f"amrex+rocm amdgpu_target={tgt}", when=f"+rocm amdgpu_target={tgt}")

        # ERF 24.10+ CMake unconditionally requests the AMReX PIC, PARTICLES, and
        # LSOLVERS components via find_package(AMReX ... COMPONENTS), regardless of
        # ERF's own +particles variant, so AMReX must always provide them. Earlier
        # releases only needed AMReX particles when ERF's +particles was set.
        # ERF is three-dimensional (ERF_DIM=3) and asks for the 3D component only;
        # dimensions=3 keeps libamrex_1d and libamrex_2d (460 MB on a CUDA build)
        # out of the dependency, while still accepting a 1,2,3 install.
        depends_on("amrex dimensions=3 +pic+particles+linear_solvers", when="@24.10:")

        # The same find_package() call pins the AMReX precision components:
        # "PDOUBLE" "DOUBLE" is hard-coded through 26.05, and 26.06 derives it
        # from ERF_PRECISION, which defaults to DOUBLE. A single-precision AMReX
        # therefore fails component detection rather than building in single;
        # from 26.06 the components follow ERF_PRECISION and AMReX must match it.
        depends_on("amrex precision=double", when="@24.10:26.05")
        for p in ("double", "single"):
            depends_on(f"amrex precision={p}", when=f"@26.06:precision={p}")
        depends_on("amrex+particles", when="@:24.09+particles")
        depends_on("amrex~particles", when="@:24.09~particles")

        depends_on("mpi", when="+mpi")
        depends_on("cuda@11.0:", when="+cuda")
        depends_on("hip", when="+rocm")
        depends_on("fftw", when="+fft")
        depends_on("hdf5+mpi", when="+hdf5")

        # Every ERF regression test pipes its plotfile through AMReX's fcompare,
        # and ERF 24.10+ looks for it at <amrex prefix>/bin/amrex_fcompare, which
        # an installed AMReX only ships with +plotfile_tools.
        depends_on("amrex+plotfile_tools", when="+tests")
        depends_on("amrex+plotfile_tools", when="+fcompare")

        # ERF 26.06 added gtest-based unit tests, which ERF enables by default
        # alongside the regression tests. Supply GoogleTest from Spack rather
        # than the bundled Submodules/googletest checkout (see patch()).
        depends_on("googletest", when="@26.06:+tests")
        # ERF's external Noah-MP CMake path uses the drivers/erf interface that
        # the standalone noahmp package builds and exports as NoahMP::noahmp.
        depends_on("noahmp@5.2.1:", when="@25.12:+noahmp")

        with when("+netcdf"):
            depends_on("amrex+mpi")
            depends_on("netcdf-c+mpi+parallel-netcdf")
            depends_on("netcdf-fortran")
            depends_on("hdf5+mpi", when="+mpi")

    # one GPU backend at a time, and OpenMP is host-only
    conflicts("+openmp", when="+cuda", msg="Cannot enable both OpenMP and CUDA")
    conflicts("+openmp", when="+rocm", msg="Cannot enable both OpenMP and HIP")
    conflicts("+openmp", when="+sycl", msg="Cannot enable both OpenMP and SYCL")
    conflicts("+cuda", when="+rocm", msg="Choose one GPU backend")
    conflicts("+cuda", when="+sycl", msg="Choose one GPU backend")
    conflicts("+rocm", when="+sycl", msg="Choose one GPU backend")
    # what ERF's CMake enforces or assumes
    conflicts("+fft", when="~mpi", msg="FFT support requires MPI")
    conflicts("+hdf5", when="~mpi", msg="AMReX HDF5 I/O is parallel HDF5 and needs MPI")
    conflicts("+rrtmgp", when="~netcdf", msg="RRTMGP requires NetCDF")
    conflicts("+rrtmgp", when="~mpi", msg="RRTMGP (EKAT) requires MPI")
    conflicts("+tools", when="~netcdf", msg="The tools require NetCDF")
    # ERF enables AMReX HDF5 whenever NetCDF is on; keep the install the same
    requires("+hdf5", when="+netcdf", msg="ERF turns on HDF5 I/O with NetCDF")
    # when each option appeared in ERF's CMake
    conflicts("precision=single", when="@:26.05", msg="single precision needs ERF 26.06+ (AMReX components follow ERF_PRECISION from there)")
    conflicts("+rrtmgp", when="@:25.09", msg="RRTMGP through EKAT needs ERF 25.10+")
    conflicts("+windfarm", when="@:26.01", msg="wind farm parameterizations need ERF 26.02+")
    conflicts("+wsm6_fort", when="@:26.04", msg="the WSM6 Fortran bridge needs ERF 26.05+")
    conflicts("+wdm6_fort", when="@:26.08", msg="the WDM6 Fortran bridge needs ERF 26.09+")
    conflicts("+tools", when="@:25.06", msg="the tools need ERF 25.07+")
    conflicts(
        "@:25.11", when="+noahmp", msg="External Noah-MP support requires ERF 25.12 or newer"
    )
    conflicts("~netcdf", when="@25.12:+noahmp", msg="Noah-MP requires NetCDF")

    def patch(self):
        # EKAT (which carries Kokkos, yaml-cpp and spdlog as its own submodules)
        # is fetched here rather than through submodules(): ERF lists it over
        # HTTPS, but EKAT lists its submodules over SSH, which an unattended
        # fetch cannot follow. Rewrite those to HTTPS and fetch what ERF builds.
        if self.spec.satisfies("+rrtmgp"):
            git = which("git", required=True)
            git("submodule", "update", "--init", "--", "Submodules/ekat")
            with working_dir(join_path("Submodules", "ekat")):
                filter_file("git@github.com:", "https://github.com/", ".gitmodules", string=True)
                git("submodule", "sync", "--quiet")
                git("submodule", "update", "--init", "--", "extern/kokkos", "extern/yaml-cpp", "extern/spdlog")

        # ERF's CMake hard-codes Noah-MP to the bundled Submodules/Noah-MP git
        # submodule via add_subdirectory(). Redirect it to the external `noahmp`
        # package, whose CMake config exports the same NoahMP::noahmp target that
        # ERF already links against in CMake/BuildERFExe.cmake.
        if self.spec.satisfies("@25.12:+noahmp"):
            cmakelists = "CMakeLists.txt"
            marker = "add_subdirectory(${NOAHMP_HOME} ${NOAHMP_BIN})"
            with open(cmakelists, encoding="utf-8") as f:
                if marker not in f.read():
                    raise InstallError("ERF CMake no longer matches the Noah-MP patch marker")
            filter_file(marker, "find_package(NoahMP REQUIRED)", cmakelists, string=True)

        # ERF 26.06+ unit tests add_subdirectory() the bundled googletest
        # checkout, which the submodules() filter above deliberately does not
        # fetch. Redirect them to the Spack-provided GoogleTest: both test
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
            self.define_from_variant("ERF_ENABLE_HDF5", "hdf5"),
            self.define_from_variant("ERF_ENABLE_SYCL", "sycl"),
            self.define_from_variant("ERF_ENABLE_RRTMGP", "rrtmgp"),
            self.define_from_variant("ERF_ENABLE_WINDFARM", "windfarm"),
            self.define_from_variant("ERF_ENABLE_WSM6_FORT", "wsm6_fort"),
            self.define_from_variant("ERF_ENABLE_WDM6_FORT", "wdm6_fort"),
            self.define_from_variant("ERF_ENABLE_TOOLS", "tools"),
            self.define("ERF_PRECISION", self.spec.variants["precision"].value.upper()),
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

        if self.spec.satisfies("@25.12:"):
            args.append(self.define_from_variant("ERF_ENABLE_NOAHMP", "noahmp"))

        # ERF derives ERF_ENABLE_EKAT from RRTMGP since 26.09; older releases read
        # it as a plain variable, which ERF's own CI sets alongside RRTMGP.
        if self.spec.satisfies("+rrtmgp"):
            args.append(self.define("ERF_ENABLE_EKAT", True))

        if "+rocm" in self.spec:
            targets = self.spec.variants["amdgpu_target"].value
            args.extend(
                [
                    self.define("ERF_ENABLE_HIP", True),
                    self.define("AMReX_AMD_ARCH", ";".join(targets)),
                    self.define("CMAKE_CXX_COMPILER", self.spec["hip"].hipcc),
                ]
            )

        if self.spec.satisfies("+netcdf") or self.spec.satisfies("+tools"):
            # ERF's CMake prepends NETCDF_DIR to CMAKE_PREFIX_PATH before its
            # FindNetCDF (nc-config / pkg-config); NetCDF_C_PATH and
            # NetCDF_FORTRAN_PATH, passed before, are read nowhere in ERF.
            args.append(self.define("NETCDF_DIR", self.spec["netcdf-c"].prefix))

        if "+cuda" in self.spec:
            # SASS for every requested architecture, PTX only for the newest: AMReX's
            # own "all" policy. SASS+PTX for each of three architectures pushed
            # erf_exec past the 2 GB small code model at link time ("relocation
            # truncated to fit: R_X86_64_PC32"). Compressed fatbins are transparent
            # at load time.
            archs = sorted(self.spec.variants["cuda_arch"].value or ["80"], key=int)
            spelled = [a if a == archs[-1] else f"{a}-real" for a in archs]
            args.append(self.define("CMAKE_CUDA_ARCHITECTURES", ";".join(spelled)))
            args.append(self.define("CMAKE_CUDA_FLAGS", "-Xfatbin=-compress-all"))
            args.extend(
                [
                    self.define("ERF_ENABLE_CUDA", "ON"),
                    self.define("CUDAToolkit_ROOT", self.spec["cuda"].prefix),
                ]
            )

        return args

    @run_after("install")
    def install_examples(self):
        """Ship two self-contained inputs so an installed ERF can be run without a
        checkout: prefix/share/erf/examples/<case>/inputs_*."""
        examples = join_path(self.prefix.share, "erf", "examples")
        for case in ("ScalarAdvDiff", "IsentropicVortex"):
            src = join_path(self.stage.source_path, "Exec", "RegTests", case)
            if os.path.isdir(src):
                install_tree(src, join_path(examples, case))

    def test_help(self):
        """erf_exec prints its usage"""
        erf_exec = which(self.prefix.bin.erf_exec)
        out = erf_exec("--help", output=str.split, error=str.split)
        assert "inputs" in out.lower()

    def test_scalar_advection(self):
        """run two steps of the uniform-velocity scalar advection case"""
        inputs = join_path(
            self.prefix.share, "erf", "examples", "ScalarAdvDiff", "inputs_advect_uniformU"
        )
        if not os.path.isfile(inputs):
            raise SkipTest("no example inputs installed for this version")
        erf_exec = which(self.prefix.bin.erf_exec)
        with working_dir(self.test_suite.current_test_cache_dir, create=True):
            erf_exec(inputs, "max_step=2", "amr.plot_int=-1", "amr.check_int=-1")

    def setup_build_environment(self, env):
        super().setup_build_environment(env)
        env.set("AMREX_HOME", self.spec["amrex"].prefix)
        if "+openmp" in self.spec:
            if "%clang" in self.spec or "%gcc" in self.spec:
                env.append_flags("CFLAGS", self.compiler.openmp_flag)
                env.append_flags("CXXFLAGS", self.compiler.openmp_flag)
                env.append_flags("FFLAGS", self.compiler.openmp_flag)
