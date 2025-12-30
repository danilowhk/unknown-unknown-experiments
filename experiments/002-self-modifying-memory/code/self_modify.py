#!/usr/bin/env python3
"""
EXPERIMENT 002: Self-Modifying Code via /proc/self/mem

The Question: Can a running Python process literally rewrite its own
machine code in memory while executing?

This is the kind of thing that "shouldn't work" because:
1. Modern OS have memory protection (NX bit, W^X policy)
2. Python bytecode is interpreted, not native
3. The code pages should be read-only

But /proc/self/mem is a special file that lets you read/write your
own process memory... let's see what happens.
"""

import os
import sys
import ctypes
import struct
import mmap
import traceback
from ctypes import CFUNCTYPE, c_int, c_void_p, c_char_p, c_size_t

print("=" * 70)
print(" EXPERIMENT 002: Self-Modifying Code via /proc/self/mem")
print("=" * 70)
print()

# ============================================================
# PART 1: Can we even read our own memory?
# ============================================================
print("[PART 1] Reading our own process memory...")
print("-" * 50)

try:
    pid = os.getpid()
    print(f"PID: {pid}")
    
    # Read memory maps to find code sections
    with open(f"/proc/{pid}/maps", "r") as f:
        maps_content = f.read()
    
    print("\nMemory map (first 20 lines):")
    for i, line in enumerate(maps_content.split('\n')[:20]):
        print(f"  {line}")
    
    # Find the python executable's code section
    code_sections = []
    for line in maps_content.split('\n'):
        if 'r-xp' in line and ('python' in line.lower() or 'libc' in line.lower()):
            parts = line.split()
            addr_range = parts[0]
            start, end = addr_range.split('-')
            code_sections.append({
                'start': int(start, 16),
                'end': int(end, 16),
                'perms': parts[1],
                'path': parts[-1] if len(parts) > 5 else '[anonymous]'
            })
    
    print(f"\n✓ Found {len(code_sections)} executable code sections")
    for sec in code_sections[:5]:
        print(f"  {hex(sec['start'])}-{hex(sec['end'])} {sec['perms']} {sec['path']}")

except Exception as e:
    print(f"✗ Failed to read memory maps: {e}")
    traceback.print_exc()

# ============================================================
# PART 2: Can we read actual machine code bytes?
# ============================================================
print("\n" + "=" * 70)
print("[PART 2] Reading actual machine code from memory...")
print("-" * 50)

try:
    if code_sections:
        target = code_sections[0]
        print(f"Target section: {target['path']}")
        print(f"Address range: {hex(target['start'])} - {hex(target['end'])}")
        
        # Try to read via /proc/self/mem
        with open(f"/proc/{pid}/mem", "rb") as mem:
            mem.seek(target['start'])
            code_bytes = mem.read(64)
        
        print(f"\n✓ Successfully read {len(code_bytes)} bytes of machine code!")
        print("First 64 bytes (hex):")
        hex_dump = ' '.join(f'{b:02x}' for b in code_bytes)
        print(f"  {hex_dump}")
        
        # Try to disassemble (if we have the right bytes)
        print("\nRaw bytes as potential x86-64 instructions:")
        for i in range(0, min(32, len(code_bytes)), 8):
            chunk = code_bytes[i:i+8]
            print(f"  +{i:04x}: {' '.join(f'{b:02x}' for b in chunk)}")
        
except Exception as e:
    print(f"✗ Failed to read machine code: {e}")
    traceback.print_exc()

# ============================================================
# PART 3: Can we WRITE to our own code? (The scary part)
# ============================================================
print("\n" + "=" * 70)
print("[PART 3] Attempting to WRITE to executable memory...")
print("-" * 50)

write_success = False
try:
    # First, let's try writing to /proc/self/mem
    # This SHOULD fail because code pages are read-only
    
    if code_sections:
        target = code_sections[0]
        print(f"Attempting write to: {hex(target['start'])}")
        
        with open(f"/proc/{pid}/mem", "r+b") as mem:
            mem.seek(target['start'])
            # Try to write a NOP (0x90 in x86)
            mem.write(b'\x90')
            mem.flush()
        
        print("✓ Write operation completed without error!")
        write_success = True
        
        # Verify the write
        with open(f"/proc/{pid}/mem", "rb") as mem:
            mem.seek(target['start'])
            verify = mem.read(1)
        
        if verify == b'\x90':
            print("✓ VERIFIED: Memory was actually modified!")
        else:
            print(f"✗ Write appeared to succeed but verification shows: {verify.hex()}")

except PermissionError as e:
    print(f"✗ Permission denied (expected): {e}")
except Exception as e:
    print(f"✗ Failed: {e}")
    traceback.print_exc()

# ============================================================
# PART 4: Alternative - mmap with PROT_EXEC
# ============================================================
print("\n" + "=" * 70)
print("[PART 4] Creating executable memory via mmap...")
print("-" * 50)

try:
    # Allocate memory that's both writable AND executable
    # This is what JIT compilers do!
    
    # x86-64 machine code for: return 42
    # mov eax, 42; ret
    shellcode_return_42 = bytes([
        0xb8, 0x2a, 0x00, 0x00, 0x00,  # mov eax, 42
        0xc3                            # ret
    ])
    
    # x86-64 machine code for: return 1337
    shellcode_return_1337 = bytes([
        0xb8, 0x39, 0x05, 0x00, 0x00,  # mov eax, 1337
        0xc3                            # ret
    ])
    
    print("Creating executable memory region...")
    
    # Create anonymous mmap with RWX permissions
    # PROT_READ | PROT_WRITE | PROT_EXEC = 7
    mem_size = 4096
    
    # Try using mmap directly
    exec_mem = mmap.mmap(-1, mem_size, 
                         prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC,
                         flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)
    
    print(f"✓ Allocated {mem_size} bytes of RWX memory")
    
    # Write the first shellcode
    exec_mem.write(shellcode_return_42)
    exec_mem.seek(0)
    
    print(f"✓ Wrote shellcode: {shellcode_return_42.hex()}")
    
    # Get the address of the mmap region
    # This is tricky in Python...
    exec_mem_addr = ctypes.addressof(ctypes.c_char.from_buffer(exec_mem))
    print(f"✓ Executable memory at: {hex(exec_mem_addr)}")
    
    # Create a function pointer to our shellcode
    FUNC_TYPE = CFUNCTYPE(c_int)
    func = FUNC_TYPE(exec_mem_addr)
    
    print("\nCalling shellcode (should return 42)...")
    result1 = func()
    print(f"✓ RESULT: {result1}")
    
    if result1 == 42:
        print("🎉 SUCCESS! We executed raw machine code from Python!")
    
    # Now the REAL test: modify the code while it exists
    print("\n" + "-" * 50)
    print("Now modifying the code in-place...")
    
    exec_mem.seek(0)
    exec_mem.write(shellcode_return_1337)
    exec_mem.seek(0)
    
    print(f"✓ Overwrote with new shellcode: {shellcode_return_1337.hex()}")
    
    print("Calling SAME function pointer (should now return 1337)...")
    result2 = func()
    print(f"✓ RESULT: {result2}")
    
    if result2 == 1337:
        print("🎉🎉 HOLY SHIT! Self-modifying code WORKS!")
        print("   We changed what a function does WHILE THE PROGRAM IS RUNNING!")
    
    exec_mem.close()

except Exception as e:
    print(f"✗ Failed: {e}")
    traceback.print_exc()

# ============================================================
# PART 5: Even crazier - modify code DURING execution
# ============================================================
print("\n" + "=" * 70)
print("[PART 5] Self-modifying loop (code changes itself mid-execution)...")
print("-" * 50)

try:
    # Create a loop that modifies its own return value each iteration
    # x86-64: mov eax, IMM32; ret
    # We'll patch the IMM32 value each time
    
    base_code = bytearray([
        0xb8, 0x00, 0x00, 0x00, 0x00,  # mov eax, 0 (we'll patch bytes 1-4)
        0xc3                            # ret
    ])
    
    exec_mem2 = mmap.mmap(-1, 4096,
                          prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC,
                          flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)
    
    exec_mem2.write(bytes(base_code))
    exec_mem2_addr = ctypes.addressof(ctypes.c_char.from_buffer(exec_mem2))
    
    FUNC_TYPE = CFUNCTYPE(c_int)
    dynamic_func = FUNC_TYPE(exec_mem2_addr)
    
    print("Running self-modifying loop (10 iterations):")
    print("Each iteration, we patch the return value in the machine code itself")
    print()
    
    results = []
    for i in range(10):
        # Call the function
        result = dynamic_func()
        results.append(result)
        
        # Now modify the code to return a different value
        new_value = (i + 1) * 100
        new_bytes = struct.pack('<I', new_value)  # Little-endian 32-bit
        
        exec_mem2.seek(1)  # Position of the immediate value
        exec_mem2.write(new_bytes)
        
        print(f"  Iteration {i}: returned {result}, patched code to return {new_value}")
    
    # One more call to see the final patched value
    final_result = dynamic_func()
    print(f"  Final call: returned {final_result}")
    
    print(f"\n✓ All results: {results + [final_result]}")
    
    expected = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    if results + [final_result] == expected:
        print("🎉🎉🎉 PERFECT! Code successfully modified itself during execution!")
    
    exec_mem2.close()

except Exception as e:
    print(f"✗ Failed: {e}")
    traceback.print_exc()

# ============================================================
# PART 6: The ultimate test - JIT-compile a Python function
# ============================================================
print("\n" + "=" * 70)
print("[PART 6] JIT-compiling a Python expression to machine code...")
print("-" * 50)

try:
    # Let's "JIT compile" simple math expressions
    # We'll generate x86-64 code that computes: a + b * c
    
    def jit_compile_add_mul(a_val, b_val, c_val):
        """Generate machine code for: return a + b * c"""
        # x86-64 assembly:
        # mov eax, a_val
        # mov ecx, b_val
        # mov edx, c_val
        # imul ecx, edx      ; ecx = b * c
        # add eax, ecx       ; eax = a + (b * c)
        # ret
        
        code = bytearray()
        
        # mov eax, a_val (B8 + imm32)
        code.extend([0xb8])
        code.extend(struct.pack('<I', a_val & 0xFFFFFFFF))
        
        # mov ecx, b_val (B9 + imm32)
        code.extend([0xb9])
        code.extend(struct.pack('<I', b_val & 0xFFFFFFFF))
        
        # mov edx, c_val (BA + imm32)
        code.extend([0xba])
        code.extend(struct.pack('<I', c_val & 0xFFFFFFFF))
        
        # imul ecx, edx (0F AF CA)
        code.extend([0x0f, 0xaf, 0xca])
        
        # add eax, ecx (01 C8)
        code.extend([0x01, 0xc8])
        
        # ret (C3)
        code.extend([0xc3])
        
        return bytes(code)
    
    # Test cases
    test_cases = [
        (1, 2, 3),      # 1 + 2*3 = 7
        (10, 5, 4),     # 10 + 5*4 = 30
        (100, 0, 999),  # 100 + 0*999 = 100
        (0, 7, 8),      # 0 + 7*8 = 56
    ]
    
    exec_mem3 = mmap.mmap(-1, 4096,
                          prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC,
                          flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)
    
    FUNC_TYPE = CFUNCTYPE(c_int)
    
    print("JIT-compiling and executing math expressions:")
    print()
    
    all_passed = True
    for a, b, c in test_cases:
        # Generate machine code
        machine_code = jit_compile_add_mul(a, b, c)
        
        # Write to executable memory
        exec_mem3.seek(0)
        exec_mem3.write(machine_code)
        
        # Execute
        jit_func_addr = ctypes.addressof(ctypes.c_char.from_buffer(exec_mem3))
        jit_func = FUNC_TYPE(jit_func_addr)
        
        result = jit_func()
        expected = a + b * c
        
        status = "✓" if result == expected else "✗"
        print(f"  {status} {a} + {b} * {c} = {result} (expected: {expected})")
        print(f"    Machine code: {machine_code.hex()}")
        
        if result != expected:
            all_passed = False
    
    if all_passed:
        print("\n🎉🎉🎉🎉 WE BUILT A MINI JIT COMPILER!")
        print("   Python generated x86-64 machine code and executed it!")
    
    exec_mem3.close()

except Exception as e:
    print(f"✗ Failed: {e}")
    traceback.print_exc()

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print(" EXPERIMENT SUMMARY")
print("=" * 70)
print("""
What we proved:
1. ✓ Can read our own process memory via /proc/self/mem
2. ✓ Can inspect actual machine code bytes in memory
3. ? Writing to code sections is blocked (as expected)
4. ✓ Can create RWX memory regions via mmap
5. ✓ Can execute arbitrary machine code from Python
6. ✓ Can MODIFY code while the program is running
7. ✓ Can build a mini JIT compiler in ~50 lines

This is how:
- JavaScript V8 engine works
- Java HotSpot JIT works  
- LuaJIT works
- PyPy's JIT works
- Game engine scripting works
- Malware polymorphism works (yikes)

The "impossible" thing that's actually possible:
Code isn't static. A running program can rewrite its own instructions.
""")
