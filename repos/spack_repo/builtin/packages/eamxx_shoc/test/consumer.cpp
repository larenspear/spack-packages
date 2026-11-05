#include <shoc_functions.hpp>
#include <Kokkos_Core.hpp>
#include <cmath>
#include <type_traits>

int main(int argc, char** argv) {
  using F = scream::shoc::Functions<scream::Real, scream::DefaultDevice>;
  static_assert(std::is_same_v<scream::Real, double>);
  static_assert(F::Spack::n == 1);
  Kokkos::initialize(argc, argv);
  int failures = 0;
  {
    F::view_2d<F::Spack> tke("tke", 2, 4);
    auto host = Kokkos::create_mirror_view(tke);
    constexpr double minimum = 0.0004; // SHOC's documented minimum TKE, m2/s2.
    for (int col = 0; col < 2; ++col) {
      host(col, 0)[0] = -1.0;
      host(col, 1)[0] = 0.0;
      host(col, 2)[0] = minimum;
      host(col, 3)[0] = 0.5 + col;
    }
    Kokkos::deep_copy(tke, host);
    // This dispatch function is defined in the installed library, not this TU.
    F::check_tke_disp(2, 4, tke);
    Kokkos::deep_copy(host, tke);
    for (int col = 0; col < 2; ++col)
      for (int lev = 0; lev < 4; ++lev) {
        const double expected = lev == 3 ? 0.5 + col : minimum;
        if (!std::isfinite(host(col, lev)[0]) || host(col, lev)[0] != expected)
          ++failures;
      }
  }
  Kokkos::finalize();
  return failures ? 1 : 0;
}
