#!/usr/bin/env python3
"""
Validation script: Prove that RWX memory regions actually exist
and that we can verify the machine code bytes.
"""
import mmap
import ctypes
import struct

print("=" * 60)
print("VALIDATION: Proving RWX memory and code execution")
print("=" * 60)

# Create RWX region
mem = mmap.mmap(-1, 4096,
                prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC,
                flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)

# Write code for: return 0xDEADBEEF
code = bytes([0xb8, 0xef, 0xbe, 0xad, 0xde, 0xc3])  # mov eax, 0xDEADBEEF; ret
mem.write(code)

# Verify bytes were written
mem.seek(0)
read_back = mem.read(6)
print(f"Written bytes:  {code.hex()}")
print(f"Read back:      {read_back.hex()}")
print(f"Match: {code == read_back}")

# Execute and verify return value
mem_addr = ctypes.addressof(ctypes.c_char.from_buffer(mem))
func = ctypes.CFUNCTYPE(ctypes.c_uint32)(mem_addr)
result = func()

print(f"\nExecuted function returned: {hex(result)}")
print(f"Expected: 0xdeadbeef")
print(f"Match: {result == 0xDEADBEEF}")

# Show memory map entry
import os
pid = os.getpid()
with open(f"/proc/{pid}/maps") as f:
    for line in f:
        if 'rwxp' in line:  # Find RWX regions
            print(f"\nRWX memory region found in /proc/{pid}/maps:")
            print(f"  {line.strip()}")
            break

mem.close()
print("\n✓ Validation complete")
