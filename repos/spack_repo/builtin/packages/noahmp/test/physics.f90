program physics
  use iso_c_binding, only: c_double
  use ieee_arithmetic, only: ieee_is_finite
  use Machine, only: kind_noahmp
  use PiecewiseLinearInterp1dMod, only: PiecewiseLinearInterp1d
  implicit none
  real(kind_noahmp) :: x(3), y(3), result
  integer :: i

  ! The installed C++ headers expose double*, regardless of build flags.
  if (kind_noahmp /= c_double) error stop 'Fortran/C++ precision mismatch'
  x = [0.0_kind_noahmp, 1.0_kind_noahmp, 2.0_kind_noahmp]
  y = 2.0_kind_noahmp * x + 1.0_kind_noahmp
  do i = -1, 5
    call PiecewiseLinearInterp1d(3, x, y, real(i, kind_noahmp)/2, result)
    if (.not. ieee_is_finite(result)) error stop 'Nonfinite interpolation'
    ! Binary-exact inputs and arithmetic: linear interpolation/extrapolation
    ! of y = 2*x + 1 at x = i/2 must return i+1 exactly.
    if (result /= real(i+1, kind_noahmp)) error stop 'Incorrect interpolation'
  end do
end program physics
