#!/usr/bin/env python3
"""
EXTREME VALIDATION: JIT-compile Fibonacci to raw x86-64 machine code
This proves we can generate non-trivial algorithms as machine code.
"""
import mmap
import ctypes

print("=" * 60)
print("EXTREME VALIDATION: JIT-compiled Fibonacci")
print("=" * 60)

# Simpler approach: iterative Fibonacci
# int fib(int n) {
#     if (n <= 1) return n;
#     int a = 0, b = 1, temp;
#     for (int i = 2; i <= n; i++) { temp = a+b; a = b; b = temp; }
#     return b;
# }

# Let me build this more carefully with correct offsets
fibonacci_code = bytearray()

# edi = n (first arg in System V ABI)

# cmp edi, 1
fibonacci_code.extend([0x83, 0xff, 0x01])
# jle to return_n (we'll patch this)
fibonacci_code.extend([0x7e, 0x00])  # placeholder, offset 4
jle_patch_pos = len(fibonacci_code) - 1

# xor eax, eax  (a = 0)
fibonacci_code.extend([0x31, 0xc0])

# mov edx, 1  (b = 1)
fibonacci_code.extend([0xba, 0x01, 0x00, 0x00, 0x00])

# mov ecx, 2  (i = 2)
fibonacci_code.extend([0xb9, 0x02, 0x00, 0x00, 0x00])

# loop_start:
loop_start = len(fibonacci_code)

# mov esi, edx  (temp = b)
fibonacci_code.extend([0x89, 0xd6])

# add esi, eax  (temp = a + b)
fibonacci_code.extend([0x01, 0xc6])

# mov eax, edx  (a = b)
fibonacci_code.extend([0x89, 0xd0])

# mov edx, esi  (b = temp)
fibonacci_code.extend([0x89, 0xf2])

# inc ecx  (i++)
fibonacci_code.extend([0xff, 0xc1])

# cmp ecx, edi  (i <= n?)
fibonacci_code.extend([0x39, 0xf9])

# jle loop_start
loop_end = len(fibonacci_code)
offset_to_loop = loop_start - (loop_end + 2)  # +2 for jle instruction size
fibonacci_code.extend([0x7e, offset_to_loop & 0xff])

# mov eax, edx  (return b)
fibonacci_code.extend([0x89, 0xd0])

# ret
fibonacci_code.extend([0xc3])

# return_n: (for n <= 1, return n)
return_n_pos = len(fibonacci_code)

# mov eax, edi  (return n)
fibonacci_code.extend([0x89, 0xf8])

# ret
fibonacci_code.extend([0xc3])

# Patch the jle offset
jle_target_offset = return_n_pos - (jle_patch_pos + 1)
fibonacci_code[jle_patch_pos] = jle_target_offset & 0xff

fibonacci_code = bytes(fibonacci_code)

print(f"Fibonacci machine code ({len(fibonacci_code)} bytes):")
print(f"  {fibonacci_code.hex()}")

# Disassembly-like view
print("\nByte-by-byte breakdown:")
print("  Offset  Bytes           Meaning")
print("  ------  --------------  -------------------------")
idx = 0
annotations = [
    (3, "cmp edi, 1"),
    (2, f"jle +{jle_target_offset} (to return_n)"),
    (2, "xor eax, eax (a=0)"),
    (5, "mov edx, 1 (b=1)"),
    (5, "mov ecx, 2 (i=2)"),
    (2, "mov esi, edx"),
    (2, "add esi, eax"),
    (2, "mov eax, edx (a=b)"),
    (2, "mov edx, esi (b=temp)"),
    (2, "inc ecx"),
    (2, "cmp ecx, edi"),
    (2, "jle loop"),
    (2, "mov eax, edx (return b)"),
    (1, "ret"),
    (2, "mov eax, edi (return n)"),
    (1, "ret"),
]
for size, desc in annotations:
    chunk = fibonacci_code[idx:idx+size]
    print(f"  {idx:04x}    {chunk.hex():<14}  {desc}")
    idx += size

# Create executable memory
mem = mmap.mmap(-1, 4096,
                prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC,
                flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)

mem.write(fibonacci_code)
mem_addr = ctypes.addressof(ctypes.c_char.from_buffer(mem))

# Create function with int argument
FUNC_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)
fib_jit = FUNC_TYPE(mem_addr)

# Python reference implementation
def fib_python(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

print("\nComparing JIT vs Python Fibonacci:")
print("-" * 40)

all_match = True
for n in range(20):
    jit_result = fib_jit(n)
    py_result = fib_python(n)
    match = "✓" if jit_result == py_result else "✗"
    print(f"  fib({n:2d}) = {jit_result:5d} (Python: {py_result:5d}) {match}")
    if jit_result != py_result:
        all_match = False

print("-" * 40)
if all_match:
    print("🎉 ALL 20 VALUES MATCH!")
    print("   We successfully JIT-compiled Fibonacci to x86-64!")
else:
    print("✗ Some values don't match - debugging needed")

# Performance comparison
import time

if all_match:
    print("\nPerformance comparison (fib(30) x 100000):")
    n = 30

    start = time.perf_counter()
    for _ in range(100000):
        fib_jit(n)
    jit_time = time.perf_counter() - start

    start = time.perf_counter()
    for _ in range(100000):
        fib_python(n)
    py_time = time.perf_counter() - start

    print(f"  JIT:    {jit_time:.4f}s")
    print(f"  Python: {py_time:.4f}s")
    print(f"  Speedup: {py_time/jit_time:.1f}x faster")

mem.close()
