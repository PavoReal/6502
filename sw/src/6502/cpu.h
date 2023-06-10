#pragma once

#include "common.h"

namespace cpu_6502
{
    typedef u8 (*external_memory_read_func_t)(u16);
    typedef void (*external_memory_write_func_t)(u16, u8);

    struct cpu_6502_t
    {
        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        // Types
        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        struct regs_t
        {
            u8 A;     // accumulator
            u8 X;     // holds loop counters or offsets for indirect addressing
            u8 Y;     // similar to the X register. It is used for holding loop counters or offsets, but for different instructions
            u16 PC;   // program counter 
            u16 S: 9; // stack pointer
            u8 P;     // processor status 
        };

        enum status_bit_t
        {
            NEGATIVE = (1 << 7),
            OVERFLOW = (1 << 6),
            CONSTANT = (1 << 5),
            BREAK    = (1 << 4),
            DECIMAL  = (1 << 3),
            INTERRUPT= (1 << 2),
            ZERO     = (1 << 1),
            CARRY    = (1 << 0)
        };

        typedef u16 (*addressing_mode_decode_func_t)(void); // Used to decode the addressing mode of an instruction
        typedef void (*opcode_exec_func_t)(u16);            // Used to execute an instruction

        // For each instruction we need to know how to handle the addressing and execution
        struct instruction_t
        {
            addressing_mode_decode_func_t decode;
            opcode_exec_func_t exec;
        };

        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        // Vars
        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        std::array<instruction_t, 256> instr_map; // instruction map
        regs_t regs;                              //

        external_memory_read_func_t  ext_read;  // handler for external memory reads
        external_memory_write_func_t ext_write; // handler for external memory writes

        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        // Funcs
        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        // Memory reads and write to external memory are handled separately from the cpu 
        cpu_6502_t(external_memory_read_func_t read, external_memory_write_func_t write);

        void Execute(instruction_t instr);
        void Reset(void);

        void Nop(u16 addr);
    };
};

