#include <stdio.h>
#include <stdint.h>

typedef uint8_t  u8;
typedef uint16_t u16;
typedef uint32_t u32;

typedef int8_t  s8;
typedef int16_t s16;
typedef int32_t s32;

struct __attribute__((packed)) cpu_6502_t
{
    union
    {
        struct 
        {
            u8 A;
            u8 X;
            u8 Y;
            u16 PC;
            u16 S: 9;
        } regs;
    };
};

void 
SetInitialCPUState(cpu_6502_t &cpu)
{
    cpu.regs.A = 0;
    cpu.regs.X = 0;
    cpu.regs.Y = 0;
    cpu.regs.PC = 0;
    cpu.regs.S = 0;
}

int 
main(void)
{
    printf("Hello World!\n");

    cpu_6502_t cpu = {};
    SetInitialCPUState(cpu);

    return 0;
}
