#pragma once

#include <stdint.h>
#include <array>

#define UNUSED(x) (void)(x)

namespace cpu_6502
{
    typedef uint8_t  u8;
    typedef uint16_t u16;
    typedef uint32_t u32;

    typedef int8_t  s8;
    typedef int16_t s16;
    typedef int32_t s32;

    inline u8 
    GetBit(u8 byte, u8 bit)
    {
        return (byte >> bit) & 1;
    }

    inline u8 
    SetBit(u8 byte, u8 bit, u8 value)
    {
        return (byte & ~(1 << bit)) | (value << bit);
    }
}
