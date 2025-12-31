# Beginner's Guide to Experiment #003: Runtime C Compilation

Welcome! This experiment might seem like magic, so this guide breaks down the core concepts. Our goal was to see if a Python script could write, compile, and run C code on its own. It worked, and here’s how.

## Core Concepts Explained

### 1. Interpreted vs. Compiled Languages

Imagine you have a recipe. There are two ways to follow it:

- **Interpreted (like Python):** You have a chef (the *interpreter*) who reads the recipe line-by-line and performs each action immediately. It's flexible and easy to start, but the chef has to read every time you cook.
- **Compiled (like C):** You first translate the entire recipe into a set of highly optimized, pre-planned instructions for a robot (the *CPU*). This translation process is called *compiling*. The next time you want to cook, the robot executes the instructions directly, which is incredibly fast. The compiled instructions are saved in a machine-readable file (an *executable* or a *library*).

This experiment blurs the lines. Our Python script acts as the chef, but instead of cooking, it writes a new, super-efficient recipe and gives it to a robot to execute for the hard parts.

### 2. What is a Shared Library (`.so` file)?

A shared library (or `.so` file on Linux) is a compiled package of code that can be shared and used by multiple programs. It's like a toolkit of pre-built, high-performance functions.

Instead of compiling our C code into a standalone program, we compile it into a `.so` file. This allows our main Python script to load and use the functions inside it *dynamically*—that is, whenever it needs them.

### 3. The Key Tools We Used

Our Python script orchestrated a few key tools to pull this off:

| Tool | Purpose | Analogy |
| :--- | :--- | :--- |
| **`subprocess`** | Allows a Python script to run command-line programs. | The script's ability to pick up a phone and give instructions to other tools, like the compiler. |
| **`gcc`** | The **G**NU **C** **C**ompiler. This is the program that translates our C source code into a machine-readable shared library (`.so` file). | A master translator who converts our C recipe into the robot's language. |
| **`ctypes`** | A built-in Python library that lets Python call functions inside shared libraries. | A universal adapter that lets our Python chef plug in and control the C-language robot. |
| **`tempfile`** | Creates temporary files and directories that are automatically cleaned up. | A disposable notepad for the script to write down the C code before handing it to the compiler. |

### 4. What's Happening in the Code?

The process unfolds in a clear sequence:

1.  **Generate C Code:** The Python script holds the C code as a simple, multi-line string.
2.  **Write to File:** It uses `tempfile` to save this string into a real file named `generated.c`.
3.  **Compile with `gcc`:** It uses `subprocess` to call `gcc`, telling it to compile `generated.c` into a shared library named `generated.so`.
4.  **Load with `ctypes`:** It uses `ctypes.CDLL()` to load the `generated.so` file into the running Python program.
5.  **Define Signatures:** It tells `ctypes` what the C functions look like (e.g., `add` takes two integers and returns an integer). This is crucial for Python to send and receive data correctly.
6.  **Execute:** The script can now call the C functions (like `lib.add(42, 58)`) as if they were Python functions, but they run at native C speed.

### 5. The 
Impossible" Feats: `rdtsc` and Stack Addresses

Our C code did two things that are normally out of reach for Python:

-   **`get_cpu_cycles()`:** This function uses a special assembly instruction (`rdtsc` - Read Time-Stamp Counter). It directly asks the CPU for its internal clock count, giving us a hyper-precise way to measure time. This is a low-level hardware feature.
-   **`get_stack_address()`:** This function finds the memory address of a local variable. This gives us a peek into how the program is laid out in the computer's RAM, something Python normally abstracts away entirely.

Being able to do this from a Python script is the core of the "unknown-unknown" discovery. We used Python's high-level flexibility to orchestrate the creation and execution of very low-level, high-performance code.

## Why Was It So Much Faster?

The final test, calculating π, showed the C code was nearly **100 times faster** than the pure Python equivalent. This is because:

-   The C code was compiled to native machine instructions that the CPU runs directly.
-   The Python code had to be interpreted line-by-line at runtime, adding a huge amount of overhead for each simple calculation.

This experiment proves that you can have the best of both worlds: Python's ease of use and C's raw performance, all in one program.
