#include <stdio.h>

#include "6502/cpu.h"
#include "6502/compiler.h"

using namespace cpu_6502;

u8
read(u16 addr)
{
    fprintf(stdout, "read: addr = %04x\n", addr);
    return 0;
}

void
write(u16 addr, u8 data)
{
    fprintf(stdout, "write: addr = %04x, data = %02x\n", addr, data);
    return;
}

int 
main(void)
{
    printf("Hello World!\n");

    cpu_6502_t cpu = cpu_6502_t(&read, &write);

    return 0;
}
