# Beginner's Guide to Running Code from an Image

Welcome! This guide breaks down our "executable image" experiment. We proved that you can hide real, runnable computer code inside a simple PNG image. It sounds like science fiction, but it's very real. Let's explore how.

## The Big Idea: What Did We Actually Do?

In short, we took a tiny computer program, converted it into raw bytes (machine code), and stored those bytes as the colors of pixels in a PNG image. Then, we wrote a Python script to read the image, extract the bytes, and tell the computer's processor to run them.

The result? The image itself printed the message "Hello from image!" to the screen.

## Core Concepts for Beginners

To understand how this works, let's demystify a few key ideas.

### 1. What is Machine Code (or "Shellcode")?

Think of machine code as the native language of your computer's processor (the CPU). It's not human-readable like Python or JavaScript. Instead, it's a sequence of raw numbers (bytes) that give the CPU direct instructions, like "put this number here" or "add these two numbers."

In our experiment, we created a tiny piece of machine code called **shellcode**. This specific shellcode tells the Linux operating system to perform a `write` action to the screen.

| Instruction (Human-Friendly) | Raw Machine Code (Bytes) |
| :--- | :--- |
| `mov rax, 1` (Prepare to write) | `48c7c001000000` |
| `mov rdi, 1` (Write to screen) | `48c7c701000000` |
| `lea rsi, [address]` (Use our message) | `488d350a000000` |
| `mov rdx, 18` (Message is 18 bytes) | `48c7c212000000` |
| `syscall` (Execute the write!) | `0f05` |
| `ret` (Return to our script) | `c3` |

This is the program we hid in our image.

### 2. How Can an Image Store Code?

An image file is just a structured collection of bytes. A PNG file, for example, stores information about its dimensions (width and height) and the color of each pixel. A color is typically represented by three numbers: Red, Green, and Blue (RGB).

- Each RGB value is a number from 0 to 255 (which is one byte).

We used a simple trick: we stored each byte of our machine code in the **Red** channel of a pixel. The Green and Blue channels were left as 0. So, if the first byte of our code was `72` (the number for `H`), the first pixel's color would be `(R=72, G=0, B=0)`. We did this for all 49 bytes of our code, creating a tiny 8x7 pixel image.

![Zoomed-in image showing pixels containing code](../evidence/executable_code_zoomed.png)
*This is the actual image we created. Each colored square is a pixel, and its Red value is one byte of our program.* 

### 3. How Do You *Run* Code from Memory?

This is the most magical part. Your computer's operating system (like Linux or Windows) has strict rules about what is data and what is code. You can't just run any random file. 

However, with the right permissions, you can ask the OS to give you a small chunk of memory that is marked as **executable**. This is like telling the computer, "Trust me, the bytes I'm about to put here are a valid program."

Our Python script does exactly this:

1.  **`mmap` (Memory Map):** It asks the Linux kernel for a small piece of memory that is readable, writable, AND executable.
2.  **Copy:** It copies the machine code bytes (which it just read from the image pixels) into this special memory area.
3.  **`ctypes` (Function Pointer):** It creates a "function pointer," which is like a bookmark that tells the program where the executable code begins.
4.  **Execute!** It "calls" this function pointer. The CPU jumps to that memory address and starts executing the machine code instructions one by one.

When the CPU executes our shellcode, it prints "Hello from image!" and then hits the `ret` instruction, which safely returns control back to our Python script.

## Why is This a 10/10 "Wait, That's Possible?" Moment?

This experiment is surprising because it breaks our mental models of what a file is. We think of `.png` as an image and `.exe` as a program. This shows that the file extension is just a label; it's the *content* and how you *interpret* it that matters.

It demonstrates that data and code are not fundamentally different—they are both just sequences of bytes. With the right tools and permissions, you can make one behave like the other. This has profound implications, both for creating clever new kinds of software and for understanding new security threats.
