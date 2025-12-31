#!/usr/bin/env python3
"""
Experiment: Can Python generate, compile, and execute C code at runtime?

This script will:
1. Generate C source code as a string
2. Write it to a file
3. Compile it into a shared library using GCC
4. Load the compiled library dynamically
5. Call functions from it
6. All without any pre-existing compiled code!
"""

import ctypes
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

def main():
    print("=" * 80)
    print("EXPERIMENT: Runtime C Code Generation and Compilation")
    print("=" * 80)
    print()
    
    # Step 1: Generate C source code
    print("[STEP 1] Generating C source code...")
    c_source = """
#include <stdio.h>
#include <math.h>
#include <time.h>

// A simple function that adds two numbers
int add(int a, int b) {
    return a + b;
}

// A more complex function that calculates factorial
long long factorial(int n) {
    if (n <= 1) return 1;
    long long result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

// A function that does something "impossible" - direct memory manipulation
unsigned long get_stack_address() {
    int local_var;
    return (unsigned long)&local_var;
}

// A function that uses CPU timestamp counter (very low-level)
unsigned long long get_cpu_cycles() {
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((unsigned long long)hi << 32) | lo;
}

// A computationally intensive function to show real C performance
double compute_pi(int iterations) {
    double pi = 0.0;
    for (int i = 0; i < iterations; i++) {
        pi += (i % 2 == 0 ? 1.0 : -1.0) / (2 * i + 1);
    }
    return pi * 4.0;
}
"""
    
    print("Generated C source code:")
    print("-" * 80)
    print(c_source)
    print("-" * 80)
    print()
    
    # Step 2: Create temporary directory and write C file
    print("[STEP 2] Writing C source to temporary file...")
    temp_dir = tempfile.mkdtemp(prefix="runtime_c_")
    c_file = Path(temp_dir) / "generated.c"
    so_file = Path(temp_dir) / "generated.so"
    
    with open(c_file, 'w') as f:
        f.write(c_source)
    
    print(f"C source written to: {c_file}")
    print(f"Will compile to: {so_file}")
    print()
    
    # Step 3: Compile the C code into a shared library
    print("[STEP 3] Compiling C code with GCC...")
    compile_cmd = [
        "gcc",
        "-shared",           # Create shared library
        "-fPIC",            # Position Independent Code
        "-O2",              # Optimization level 2
        "-o", str(so_file), # Output file
        str(c_file)         # Input file
    ]
    
    print(f"Compile command: {' '.join(compile_cmd)}")
    
    start_compile = time.time()
    result = subprocess.run(
        compile_cmd,
        capture_output=True,
        text=True
    )
    compile_time = time.time() - start_compile
    
    print(f"Compilation took: {compile_time:.4f} seconds")
    
    if result.returncode != 0:
        print("COMPILATION FAILED!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)
    
    print("✓ Compilation successful!")
    print()
    
    # Step 4: Verify the shared library was created
    print("[STEP 4] Verifying compiled library...")
    if not so_file.exists():
        print("ERROR: Shared library file not found!")
        sys.exit(1)
    
    file_size = so_file.stat().st_size
    print(f"✓ Shared library created: {so_file}")
    print(f"  File size: {file_size} bytes")
    
    # Use 'file' command to inspect the binary
    file_info = subprocess.run(
        ["file", str(so_file)],
        capture_output=True,
        text=True
    )
    print(f"  File type: {file_info.stdout.strip()}")
    print()
    
    # Step 5: Load the compiled library dynamically
    print("[STEP 5] Loading compiled library into Python...")
    try:
        lib = ctypes.CDLL(str(so_file))
        print("✓ Library loaded successfully!")
    except Exception as e:
        print(f"ERROR loading library: {e}")
        sys.exit(1)
    print()
    
    # Step 6: Define function signatures
    print("[STEP 6] Defining function signatures...")
    
    # int add(int a, int b)
    lib.add.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.add.restype = ctypes.c_int
    
    # long long factorial(int n)
    lib.factorial.argtypes = [ctypes.c_int]
    lib.factorial.restype = ctypes.c_longlong
    
    # unsigned long get_stack_address()
    lib.get_stack_address.argtypes = []
    lib.get_stack_address.restype = ctypes.c_ulong
    
    # unsigned long long get_cpu_cycles()
    lib.get_cpu_cycles.argtypes = []
    lib.get_cpu_cycles.restype = ctypes.c_ulonglong
    
    # double compute_pi(int iterations)
    lib.compute_pi.argtypes = [ctypes.c_int]
    lib.compute_pi.restype = ctypes.c_double
    
    print("✓ Function signatures defined")
    print()
    
    # Step 7: Call the functions and verify they work!
    print("[STEP 7] Calling C functions from Python...")
    print("=" * 80)
    
    # Test add()
    print("\nTest 1: add(42, 58)")
    result = lib.add(42, 58)
    print(f"Result: {result}")
    assert result == 100, "Addition failed!"
    print("✓ Correct!")
    
    # Test factorial()
    print("\nTest 2: factorial(20)")
    result = lib.factorial(20)
    print(f"Result: {result}")
    expected = 2432902008176640000
    assert result == expected, f"Factorial failed! Expected {expected}"
    print("✓ Correct!")
    
    # Test get_stack_address() - call it twice to show it changes
    print("\nTest 3: get_stack_address() - Low-level memory access")
    addr1 = lib.get_stack_address()
    addr2 = lib.get_stack_address()
    print(f"First call:  0x{addr1:016x}")
    print(f"Second call: 0x{addr2:016x}")
    print(f"Difference:  {abs(addr1 - addr2)} bytes")
    print("✓ Successfully accessed stack memory addresses!")
    
    # Test get_cpu_cycles() - call it twice to show CPU counter
    print("\nTest 4: get_cpu_cycles() - Direct CPU instruction (RDTSC)")
    cycles1 = lib.get_cpu_cycles()
    # Do some work
    _ = sum(range(10000))
    cycles2 = lib.get_cpu_cycles()
    print(f"Before work: {cycles1}")
    print(f"After work:  {cycles2}")
    print(f"CPU cycles elapsed: {cycles2 - cycles1}")
    print("✓ Successfully executed x86 assembly instruction!")
    
    # Test compute_pi() - show C performance
    print("\nTest 5: compute_pi(10000000) - Performance comparison")
    print("Computing π using 10 million iterations...")
    
    start = time.time()
    pi_result = lib.compute_pi(10000000)
    c_time = time.time() - start
    
    print(f"Result: {pi_result:.10f}")
    print(f"C execution time: {c_time:.6f} seconds")
    
    # Compare with pure Python
    print("\nComparing with pure Python implementation...")
    start = time.time()
    pi_python = sum((1.0 if i % 2 == 0 else -1.0) / (2 * i + 1) for i in range(10000000)) * 4.0
    python_time = time.time() - start
    
    print(f"Result: {pi_python:.10f}")
    print(f"Python execution time: {python_time:.6f} seconds")
    print(f"C is {python_time / c_time:.2f}x faster!")
    print("✓ C code is significantly faster!")
    
    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE!")
    print("=" * 80)
    print("\nSUMMARY:")
    print("✓ Generated C source code from Python string")
    print("✓ Wrote C code to file")
    print("✓ Compiled C code into shared library using GCC")
    print("✓ Loaded compiled library dynamically")
    print("✓ Called C functions from Python")
    print("✓ Verified correct execution")
    print("✓ Demonstrated low-level CPU access")
    print("✓ Showed performance advantage of compiled code")
    print()
    print(f"Temporary files location: {temp_dir}")
    print("(Files will be cleaned up on next reboot)")
    print()
    print("CONCLUSION: YES, Python can generate, compile, and execute C code at runtime!")
    print("This opens up possibilities for:")
    print("  - JIT compilation for performance-critical code")
    print("  - Dynamic code generation based on runtime conditions")
    print("  - Self-optimizing programs")
    print("  - Runtime hardware-specific optimizations")

if __name__ == "__main__":
    main()
