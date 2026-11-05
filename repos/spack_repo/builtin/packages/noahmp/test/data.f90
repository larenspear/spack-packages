program data
  use mpi
  use netcdf
  implicit none
  character(len=4096) :: directory
  character(len=40), parameter :: tables(3) = [character(len=40) :: &
      'snicar_drdt_bst_fit_60_c070416.nc', &
      'snicar_optics_480bnd_c012422.nc', &
      'snicar_optics_5bnd_c013122.nc']
  integer :: i, ncid, nvars, ierr, unit
  logical :: exists

  call get_command_argument(1, directory)
  inquire(file=trim(directory)//'/NoahmpTable.TBL', exist=exists)
  if (.not. exists) error stop 'Missing parameter table'
  open(newunit=unit, file=trim(directory)//'/NoahmpTable.TBL', status='old', iostat=ierr)
  if (ierr /= 0) error stop 'Unreadable parameter table'
  close(unit)
  do i = 1, size(tables)
    call check(nf90_open(trim(directory)//'/'//trim(tables(i)), NF90_NOWRITE, ncid))
    call check(nf90_inquire(ncid, nVariables=nvars))
    if (nvars < 1) error stop 'Empty SNICAR table'
    call check(nf90_close(ncid))
  end do

  ! The driver requires MPI-IO support even on a single rank.
  call MPI_Init(ierr)
  if (ierr /= MPI_SUCCESS) error stop 'MPI_Init failed'
  call check(nf90_create('parallel.nc', ior(NF90_NETCDF4, NF90_CLOBBER), &
      ncid, comm=MPI_COMM_WORLD, info=MPI_INFO_NULL))
  call check(nf90_close(ncid))
  call MPI_Finalize(ierr)
  if (ierr /= MPI_SUCCESS) error stop 'MPI_Finalize failed'
contains
  subroutine check(status)
    integer, intent(in) :: status
    if (status /= nf90_noerr) then
      print *, trim(nf90_strerror(status))
      error stop 1
    end if
  end subroutine check
end program data
