# A Beginner's Guide to Self-Modifying Code

Welcome! This experiment might seem like something out of a sci-fi movie, but it's a real and fundamental concept in computer science. If you're new to low-level programming, this guide will walk you through what we did, why it's so mind-bending, and why it matters.

## Core Concepts: The Building Blocks

To understand this experiment, let's start with a few key ideas.

### What is Machine Code?

Imagine you have a recipe. You can read it because it's in English. But a robot chef would need that recipe translated into a series of simple, direct commands it understands, like `01101001` (turn on oven) or `11100101` (add flour).

**Machine code** is the language your computer's processor (the CPU) actually understands. It's not human-readable; it's a stream of numbers (bytes) that correspond to very basic operations like "add these two numbers," "move this data from here to there," or "jump to a different instruction."

When you write Python code like `print("Hello")`, a program called an **interpreter** reads that text and runs the corresponding, pre-written machine code instructions to make the text appear on your screen.

### What is Memory (RAM)?

Think of your computer's memory (RAM) as a giant, numbered wall of mailboxes. Each mailbox has a unique address and can hold a small piece of information (a number).

When you run a program, the operating system (OS) gives it a section of these mailboxes to use. This is where it stores everything it needs:

-   The machine code instructions for the program.
-   The data it's working with (variables, text, etc.).
-   A record of what it's currently doing.

Crucially, for security, the OS sets rules on these mailboxes. Some are marked "Read-Only" (like the ones holding the program's instructions), while others are marked "Read-Write" (for data that needs to change).

### What is a Process?

A **process** is simply a running program. When you double-click an icon, you're starting a process. Each process gets its own private set of mailboxes (memory) and thinks it has the whole computer to itself. This is a security feature called **memory isolation**—it prevents a crashed web browser from taking down your whole system.

## The Experiment: What Did We Actually Do?

Our experiment aimed to break the rules. We asked: can a running program reach into its own "Read-Only" mailboxes and change its own instructions?

### Part 1: Writing Our Own Machine Code

First, we acted as the robot chef's programmer. We manually wrote the raw machine code bytes for a simple function. For example, the machine code for a function that just returns the number `42` looks like this in the x86-64 language:

```
B8 2A 00 00 00   # This means: "Put the number 42 into the CPU's return register (EAX)"
C3               # This means: "Return from the function"
```

We created this sequence of bytes directly in our Python script.

### Part 2: Asking the OS for Special Memory

Next, we used a special OS command called `mmap` (memory map). We asked the OS for a new, empty set of mailboxes with a very unusual permission setting: **Read-Write-Execute (RWX)**.

-   **Read**: We can look at what's in the mailboxes.
-   **Write**: We can change what's in the mailboxes.
-   **Execute**: We can tell the CPU to treat the contents of the mailboxes as runnable instructions.

This is the key! Normally, memory is either for data (Read-Write) or for code (Read-Execute), but not both. Asking for RWX memory is like asking for a recipe card that you can edit *while the chef is reading it*.

### Part 3: Executing Our Code

We then did the following:

1.  **Wrote our machine code** (the bytes for `return 42`) into our special RWX mailboxes.
2.  Used Python's `ctypes` library to get the memory address (the mailbox number) of the start of our code.
3.  Told Python: "Hey, this memory address is actually a function. Please call it."

And it worked! The CPU jumped to our mailboxes, executed the instructions we put there, and returned the number 42 to our Python script.

### Part 4: The "Impossible" Part - Modifying Code On-The-Fly

This is where it gets truly wild. After running our function that returns `42`, we did this:

1.  Reached back into the *same* RWX mailboxes.
2.  **Overwrote** the bytes for `42` with the bytes for `1337`.
3.  Called the *exact same function pointer* again.

This time, it returned `1337`. We had successfully changed what the function does while the program was still running. This is **self-modifying code**.

## Why This Is a 10/10 "Wait, that's possible?" Moment

This shatters the mental model that "code is static." It proves that a program's logic is not set in stone when it's compiled. Code can be treated just like data—it can be created, manipulated, and changed dynamically.

This is the core principle behind **Just-In-Time (JIT) Compilation**. High-performance systems like the V8 JavaScript engine (in Chrome) or PyPy work like this:

1.  They start by interpreting your code slowly.
2.  They watch for functions or loops that are run many, many times (so-called "hot spots").
3.  When they find a hot spot, they run a built-in compiler that translates that piece of your high-level code (Python, JavaScript) into super-fast, optimized machine code.
4.  They then use the `mmap` trick we used to place this new machine code into executable memory.
5.  Finally, they patch the running program to call this new, faster version of the function from now on.

Our experiment is a tiny, manual version of what these sophisticated engines do automatically millions of times a second.

## What's the Catch?

With great power comes great responsibility. The ability to create and run code on the fly is also a massive security risk. It's the foundation of **polymorphic viruses**, which change their own code to avoid being detected by antivirus software.

Because of this, modern operating systems and CPUs have many layers of security to make this difficult to exploit, but the fundamental capability must exist for high-performance computing to be possible.
