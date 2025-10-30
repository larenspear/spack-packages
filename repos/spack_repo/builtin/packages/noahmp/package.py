# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install noahmp
#
# You can edit this file again by typing:
#
#     spack edit noahmp
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *

import os
import textwrap

class Noahmp(CMakePackage):
    """Noah-MP is a land surface model (LSM) using multiple options for key land-atmosphere interaction processes."""

    homepage = "https://github.com/NCAR/noahmp"
    url = "https://github.com/NCAR/noahmp/archive/refs/tags/v5.1.0.tar.gz"
    git = "https://github.com/NCAR/noahmp.git"

    maintainers("larenspear")

    version("5.1.0", sha256="45e1dd87eeffb56125a397fe82106185d989104ea9c1172d907b318c4aca7493")
    version("5.0.0", sha256="4329e065c1a9d333996d5fc81138d24a6f6d8cd4e37fb9a9ac414514c06f1243")

    variant("shared", default=True, description="Build shared library")

    depends_on("cxx", type="build")
    depends_on("fortran", type="build")

    depends_on("cmake@3.17:", type="build")

    def cmake_args(self):
        return [self.define_from_variant("BUILD_SHARED_LIBS", "shared")]

    def libs(self):
        return find_libraries(["noahmp"], root=self.prefix, shared=("+shared" in self.spec), recursive=True)
