function check_binding() result(value) bind(C)
  use iso_c_binding, only: c_int
#ifdef NOAHMP_OLD_INTERFACE
  use NoahmpIO_fi, only: NoahmpIO
#else
  use NoahmpIO_fi, only: NoahmpIO_vect
#endif
  implicit none
  integer(c_int) :: value
#ifdef NOAHMP_OLD_INTERFACE
  value = NoahmpIO(0)%nsoil
#else
  value = NoahmpIO_vect(0)%NoahmpIO(0)%nsoil
#endif
end function check_binding

function prepare_field() result(address) bind(C)
  use iso_c_binding, only: c_ptr, c_loc, c_null_ptr, c_double
  use Machine, only: kind_noahmp
#ifdef NOAHMP_OLD_INTERFACE
  use NoahmpIO_fi, only: NoahmpIO
#define BLOCK NoahmpIO(0)
#else
  use NoahmpIO_fi, only: NoahmpIO_vect
#define BLOCK NoahmpIO_vect(0)%NoahmpIO(0)
#endif
  implicit none
  type(c_ptr) :: address
  address = c_null_ptr
  if (kind_noahmp /= c_double) return
  allocate(BLOCK%XLAT(1:2,1:1))
  BLOCK%XLAT(:,1) = [1.25_kind_noahmp, -2.5_kind_noahmp]
  address = c_loc(BLOCK%XLAT)
end function prepare_field

function check_field() result(value) bind(C)
  use iso_c_binding, only: c_int
  use Machine, only: kind_noahmp
#ifdef NOAHMP_OLD_INTERFACE
  use NoahmpIO_fi, only: NoahmpIO
#else
  use NoahmpIO_fi, only: NoahmpIO_vect
#endif
  implicit none
  integer(c_int) :: value
  ! Exact binary fractions test storage interoperability, with no arithmetic.
  value = 0
  if (BLOCK%XLAT(1,1) == 1.25_kind_noahmp .and. &
      BLOCK%XLAT(2,1) == 3.75_kind_noahmp) value = 1
end function check_field
