from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack_repo.builtin.build_systems.rocm import ROCmPackage

from spack.package import *


def submodules(package):
    submodules = []

    if package.spec.satisfies("+noahmp"):
        submodules.append("Submodules/Noah-MP")
    if package.spec.satisfies("+rrtmgp"):
        # RRTMGP needs EKAT, which carries Kokkos and friends as nested submodules
        submodules.append("Submodules/RRTMGP")
        submodules.append("Submodules/ekat")

    return submodules


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

    version("develop", branch="development", submodules=submodules)
    version("26.09", tag="26.09", submodules=submodules)
    version("26.06", tag="26.06", submodules=submodules)
    version("26.05", tag="26.05", submodules=submodules)
    version("26.04", tag="26.04", submodules=submodules)
    version("26.03", tag="26.03", submodules=submodules)
    version("26.02", tag="26.02", submodules=submodules)
    version("26.01", tag="26.01", submodules=submodules)
    version("25.12", tag="25.12", submodules=submodules)
    version("25.11", tag="25.11", submodules=submodules)
    version("25.10", tag="25.10", submodules=submodules)
    version("25.08", tag="25.08", submodules=submodules)
    version("25.07", tag="25.07", submodules=submodules)
    version("25.06", tag="25.06", submodules=submodules)
    version("25.05", tag="25.05", submodules=submodules)
    version("25.04", tag="25.04", submodules=submodules)
    version("25.03", tag="25.03", submodules=submodules)
    version("25.01", tag="25.01", submodules=submodules)
    version("24.11", tag="24.11", submodules=submodules)
    version("24.10", tag="24.10", submodules=submodules)
    version("24.09", tag="24.09", submodules=submodules)
    version("24.08", tag="24.08", submodules=submodules)
    version("24.06", tag="24.06", submodules=submodules)
    version("24.05", tag="24.05", submodules=submodules)
    version("24.04", tag="24.04", submodules=submodules)
    version("24.03", tag="24.03", submodules=submodules)
    version("24.02", tag="24.02", submodules=submodules)
    version("24.01", tag="24.01", submodules=submodules)
    version("23.12", tag="23.12", submodules=submodules)
    version("23.11", tag="23.11", submodules=submodules)
    version("23.10", tag="23.10", submodules=submodules)

    variant("mpi", default=True, description="Enable MPI support")
    variant("openmp", default=False, description="Enable OpenMP support")
    variant("netcdf", default=False, description="Enable NetCDF support")
    variant("particles", default=False, description="Enable particle support")
    variant("multiblock", default=False, description="Enable multiblock support")
    variant("tests", default=False, description="Enable tests")
    variant("fcompare", default=False, description="Enable fcompare")
    variant("fft", default=False, description="Enable FFT support")
    variant("noahmp", default=False, description="Enable Noah-MP land surface model")
    variant(
        "precision",
        default="double",
        values=("double", "single"),
        multi=False,
        description="Floating point precision of the mesh and particle data",
    )
    variant("hdf5", default=False, description="Enable HDF5 I/O (on by default with +netcdf)")
    variant("sycl", default=False, description="Enable the SYCL GPU backend (needs %oneapi)")
    variant("rrtmgp", default=False, description="Enable RTE-RRTMGP radiation (builds EKAT/Kokkos)")
    variant("windfarm", default=False, description="Enable wind farm parameterizations")
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
        # ERF's find_package(AMReX) always asks for the 3D, PIC, PARTICLES and LSOLVERS
        # components, whatever ERF_ENABLE_PARTICLES is set to, and uses the EB classes.
        depends_on("amrex dimensions=3 +pic+particles+eb+linear_solvers")
        for v in ("mpi", "openmp", "cuda", "rocm", "sycl", "hdf5"):
            depends_on(f"amrex+{v}", when=f"+{v}")
            depends_on(f"amrex~{v}", when=f"~{v}")
        for p in ("double", "single"):
            depends_on(f"amrex precision={p}", when=f"precision={p}")
        for sm in CudaPackage.cuda_arch_values:
            depends_on(f"amrex+cuda cuda_arch={sm}", when=f"+cuda cuda_arch={sm}")
        for tgt in ROCmPackage.amdgpu_targets:
            depends_on(f"amrex+rocm amdgpu_target={tgt}", when=f"+rocm amdgpu_target={tgt}")
        depends_on("mpi", when="+mpi")
        depends_on("cuda@11.0:", when="+cuda")
        depends_on("hip", when="+rocm")
        depends_on("fftw", when="+fft")
        depends_on("hdf5+mpi", when="+hdf5")

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
    # constraints ERF's CMake enforces
    conflicts("+fft", when="~mpi", msg="FFT support requires MPI")
    conflicts("+noahmp", when="~netcdf", msg="Noah-MP requires NetCDF")
    conflicts("+rrtmgp", when="~netcdf", msg="RRTMGP requires NetCDF")
    conflicts("+rrtmgp", when="~mpi", msg="RRTMGP (EKAT) requires MPI")
    conflicts("+tools", when="~netcdf", msg="The tools require NetCDF")

    def cmake_args(self):
        args = [
            self.define_from_variant("ERF_ENABLE_MPI", "mpi"),
            self.define_from_variant("ERF_ENABLE_OPENMP", "openmp"),
            self.define_from_variant("ERF_ENABLE_NETCDF", "netcdf"),
            self.define_from_variant("ERF_ENABLE_PARTICLES", "particles"),
            self.define_from_variant("ERF_ENABLE_MULTIBLOCK", "multiblock"),
            self.define_from_variant("ERF_ENABLE_TESTS", "tests"),
            self.define_from_variant("ERF_ENABLE_FCOMPARE", "fcompare"),
            self.define_from_variant("ERF_ENABLE_FFT", "fft"),
            self.define_from_variant("ERF_ENABLE_NOAHMP", "noahmp"),
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
            self.define("GIT_SUBMODULE_PROTOCOL", "https"),
            self.define("MPIEXEC_PREFLAGS", "--oversubscribe"),
        ]

        if "+netcdf" in self.spec:
            args.extend(
                [
                    self.define("NetCDF_C_PATH", self.spec["netcdf-c"].prefix),
                    self.define("NetCDF_FORTRAN_PATH", self.spec["netcdf-fortran"].prefix),
                ]
            )

        if "+rocm" in self.spec:
            targets = self.spec.variants["amdgpu_target"].value
            args.extend(
                [
                    self.define("ERF_ENABLE_HIP", "ON"),
                    self.define("AMReX_AMD_ARCH", ";".join(targets)),
                    self.define("CMAKE_CXX_COMPILER", self.spec["hip"].hipcc),
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

    @run_after("install")
    def install_examples(self):
        """Ship a few self-contained inputs files so an installed ERF can be run
        without a checkout: prefix/share/erf/examples/<case>/inputs_*."""
        examples = join_path(self.prefix.share, "erf", "examples")
        for case in ("ScalarAdvDiff", "IsentropicVortex"):
            src = join_path(self.stage.source_path, "Exec", "RegTests", case)
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
