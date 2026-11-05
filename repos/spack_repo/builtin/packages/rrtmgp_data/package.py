# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class RrtmgpData(Package):
    """Versioned gas and cloud optical coefficient tables for RRTMGP."""

    homepage = "https://github.com/E3SM-Project/rte-rrtmgp"
    url = "https://github.com/E3SM-Project/rte-rrtmgp/archive/71693e7490db0908a625eadb6ac3f23967de2c7d.tar.gz"
    maintainers("larenspear")
    license("BSD-3-Clause")
    version(
        "erf-26.11",
        url=url,
        sha256="a45c2ccdadedc71bdcf9db9e908e84bfd26b0febe8c041c695ac5ce8ca31184d",
    )

    def install(self, spec, prefix):
        mkdirp(prefix.share.rrtmgp)
        for name in (
            "rrtmgp/data/rrtmgp-data-sw-g224-2018-12-04.nc",
            "rrtmgp/data/rrtmgp-data-lw-g256-2018-12-04.nc",
            "extensions/cloud_optics/rrtmgp-cloud-optics-coeffs-sw.nc",
            "extensions/cloud_optics/rrtmgp-cloud-optics-coeffs-lw.nc",
            "examples/all-sky/rrtmgp-allsky.nc",
            "LICENSE",
        ):
            install(name, prefix.share.rrtmgp)

    def setup_run_environment(self, env):
        env.set("RRTMGP_DATA_DIR", self.prefix.share.rrtmgp)
