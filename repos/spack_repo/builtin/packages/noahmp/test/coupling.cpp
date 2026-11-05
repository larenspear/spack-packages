#include <NoahmpIO.H>

extern "C" int check_binding();
extern "C" double* prepare_field();
extern "C" int check_field();

int main() {
    NoahmpIO_vector blocks;
#ifdef NOAHMP_OLD_INTERFACE
    blocks.resize(1);
#else
    blocks.resize(1, 0);
    blocks[0].level = 0;
#endif
    blocks[0].blkid = 0;
    blocks[0].nsoil = 4;
    blocks[0].ScalarInitDefault();
    // Check that a real library call bound the Fortran pointer to this field.
    if (check_binding() != 4) return 1;
    blocks[0].nsoil = 7;
    if (check_binding() != 7) return 1;
    double* field = prepare_field();
    if (!field || field[0] != 1.25 || field[1] != -2.5) return 1;
    field[1] = 3.75;
    return check_field() == 1 ? 0 : 1;
}
