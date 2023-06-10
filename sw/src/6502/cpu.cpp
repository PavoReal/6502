#include "cpu.h"

using namespace cpu_6502;

cpu_6502_t::cpu_6502_t(external_memory_read_func_t read, external_memory_write_func_t write) :
    ext_read(read),
    ext_write(write)
{
    // Initialize instruction map
    instruction_t instr;

    for (std::size_t i = 0; i < this->instr_map.max_size(); ++i)
    {
        instr.decode = nullptr;
        instr.exec   = nullptr;

        this->instr_map[i] = instr;
    }

    // Reset cpu state
    this->Reset();
}

void
cpu_6502_t::Reset(void)
{
    // Reset registers
    this->regs.A  = 0;
    this->regs.X  = 0;
    this->regs.Y  = 0;
    this->regs.PC = 0;
    this->regs.S  = 0;
    this->regs.P  = cpu_6502_t::status_bit_t::CONSTANT;
}

void
cpu_6502_t::Execute(instruction_t instr)
{
    auto addr = instr.decode();
    instr.exec(addr);
}

void
cpu_6502_t::Nop(u16 addr)
{
    UNUSED(addr);

    return;
}