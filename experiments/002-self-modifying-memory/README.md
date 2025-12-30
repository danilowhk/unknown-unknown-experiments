# Experiment #002: Self-Modifying Code via In-Memory Execution
**Date:** 2025-12-30  
**"Wait, that's possible?" Score:** 10/10

## Question
Can a running Python process literally create new machine code in memory and execute it, effectively modifying its own behavior on the fly?

## Why It Matters
If this works, it unlocks the core principle behind Just-In-Time (JIT) compilation, the technology that makes modern languages like JavaScript (V8), Java (HotSpot), and high-performance Python (PyPy) fast. It means code isn't a static asset; it can be generated, optimized, and changed dynamically at runtime. This is the foundation for high-performance computing, dynamic language interpreters, and, on the darker side, sophisticated polymorphic malware.

## The Code
- [`code/self_modify.py`](./code/self_modify.py): The main experiment, demonstrating reading process memory, creating executable memory with `mmap`, and overwriting code in that region.
- [`code/jit_fibonacci.py`](./code/jit_fibonacci.py): An extreme validation test where a Fibonacci function is hand-compiled into raw x86-64 machine code from Python and then executed, including a performance benchmark.

## Raw Output
- [`evidence/run1_output.txt`](./evidence/run1_output.txt): First complete run of the main experiment script.
- [`evidence/run2_output.txt`](./evidence/run2_output.txt): Second run, confirming reproducibility.
- [`evidence/fibonacci_validation.txt`](./evidence/fibonacci_validation.txt): Output from the JIT Fibonacci test, showing correctness and a ~2.5x performance speedup over native Python.

## Validation
- [x] **External proof exists**: The process successfully creates a Read-Write-Execute (RWX) memory segment, which is confirmed by inspecting `/proc/self/maps`. The JIT-compiled Fibonacci code runs, produces the correct sequence, and is measurably faster than the pure Python equivalent.
- [x] **Reproducible**: Both runs of the main script produced identical, successful outcomes. The Fibonacci JIT is also stable and reproducible.
- [x] **Output contains info I couldn't have guessed**: The most stunning result is that a Python script can hand-craft a function in raw machine code, inject it into memory, and call it, resulting in a **2.5x speedup**. I was also surprised that a direct write to the code section in `/proc/self/mem` completed without an error but was silently ignored by the kernel, which is a subtle but powerful security feature.
- [x] **A skeptic would believe this**: The evidence is concrete and verifiable. The code is provided, the raw logs show it running, the output is correct, the performance difference is benchmarked, and the existence of the RWX memory region is proven via the kernel's own process filesystem.

## Confidence
🟢 **Confirmed**

## Learnings
- **What surprised me?**
  1.  **You can just ask for executable memory.** The OS allows a process to request a memory region that is simultaneously Writable and eXecutable (`RWX`) via `mmap`. I assumed this would be heavily restricted for security, but it's a standard feature required for JIT compilers.
  2.  **`ctypes` is a gateway to raw power.** Python's built-in `ctypes` library is capable of taking an arbitrary memory address and creating a callable function pointer from it. This is the magic that bridges Python's safe, interpreted world with the wild west of raw machine code.
  3.  **Python can be a JIT compiler.** We successfully built a miniature JIT compiler. The Python script generated a string of x86-64 bytes representing a function, placed it into executable memory, and ran it. This is exactly what engines like V8 do, just on a much larger scale.
  4.  **The performance gain is real and immediate.** Even for a simple, iterative Fibonacci function, executing the JIT-compiled machine code was ~2.5 times faster than the equivalent pure Python code. This isn't a theoretical concept; it's a practical speedup.

- **What new questions emerged?**
  - How do real-world JITs (like V8 or PyPy) identify which parts of the code are "hot" and worth compiling to machine code?
  - What security mechanisms (like ASLR, W^X, and SELinux) are in place to prevent this technique from being easily abused by malware?
  - Can this be done in other high-level languages like Node.js, Ruby, or even from within a web browser via WebAssembly?

- **What's the next rabbit hole?**
  - **Build a tiny JIT for a toy language.** Instead of hand-writing machine code for one function, write a Python script that parses a simple language (like Brainfuck or a small arithmetic language) and generates machine code for it on the fly.
  - **Explore security hardening.** Investigate how kernel security features like `seccomp-bpf` can be used to create a sandbox that explicitly forbids a process from creating executable memory, effectively blocking JIT compilation.
  - **Cross-language JIT.** Can a Python script generate machine code that is then called by a completely different process, written in another language like C or Go?
