#include <catch2/catch.hpp>
#include <ekat_comm.hpp>
#include <ekat_pack.hpp>
#include <ekat_yaml.hpp>
#include <ekat_tridiag.hpp>
#include <ekat_expression_eval.hpp>
#include <spdlog/spdlog.h>
#include <Kokkos_Core.hpp>

TEST_CASE("Installed EKAT exports support a complete consumer") {
  ekat::Comm comm(MPI_COMM_WORLD);
  const auto filename = "consumer-" + std::to_string(comm.rank()) + ".yaml";
  ekat::ParameterList p("input");
  p.set("count", 8);
  p.set("coefficient", 0.5);
  ekat::write_yaml_file(filename, p);
  auto recovered = ekat::parse_yaml_file(filename);
  REQUIRE(recovered.get<int>("count") == 8);
  REQUIRE(recovered.get<double>("coefficient") == 0.5);

  Kokkos::View<int*> values("values", 8);
  Kokkos::parallel_for("fill", 8, KOKKOS_LAMBDA(const int i) { values(i) = i + 1; });
  int sum = 0;
  Kokkos::parallel_reduce("sum", 8, KOKKOS_LAMBDA(const int i, int& result) {
    result += values(i);
  }, sum);
  REQUIRE(sum == 36);

  ekat::Pack<double, 4> x(2.0), y(0.5);
  const auto z = x * y + y;
  for (int i = 0; i < 4; ++i) REQUIRE(z[i] == 1.5);
  int reduced = 0;
  comm.all_reduce(&sum, &reduced, 1, MPI_SUM);
  REQUIRE(reduced == 36 * comm.size());
  spdlog::info("EKAT consumer passed: {} ranks, sum {}", comm.size(), reduced);
}
