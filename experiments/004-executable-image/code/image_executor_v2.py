#!/usr/bin/env python3
"""
Experiment: Can we execute machine code extracted from a PNG image?

This tests whether we can:
1. Encode x86 machine code into image pixels
2. Extract it back from the image
3. Load it into memory and execute it

This is a "wait, THAT'S possible?!" moment because images are typically
just data, but here we're treating pixel values as executable instructions.
"""

import os
import sys
from PIL import Image
import ctypes
import mmap
import struct

# Evidence directory
EVIDENCE_DIR = "/home/ubuntu/unknown-unknown-experiments/experiments/004-executable-image/evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def create_hello_world_shellcode():
    """
    Create x86-64 shellcode that writes "Hello from image!" to stdout
    
    This is raw machine code that:
    1. Sets up a write() syscall
    2. Writes our message to file descriptor 1 (stdout)
    3. Returns cleanly (no exit!)
    """
    # x86-64 Linux shellcode to write "Hello from image!\n" to stdout
    shellcode = bytes([
        # write(1, message, 18)
        0x48, 0xc7, 0xc0, 0x01, 0x00, 0x00, 0x00,  # mov rax, 1 (sys_write)
        0x48, 0xc7, 0xc7, 0x01, 0x00, 0x00, 0x00,  # mov rdi, 1 (stdout)
        0x48, 0x8d, 0x35, 0x0a, 0x00, 0x00, 0x00,  # lea rsi, [rip+10] (message)
        0x48, 0xc7, 0xc2, 0x12, 0x00, 0x00, 0x00,  # mov rdx, 18 (length)
        0x0f, 0x05,                                # syscall
        
        # return (instead of exit)
        0xc3,                                      # ret
        
        # Message string
        0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x20, 0x66, 0x72,  # "Hello fr"
        0x6f, 0x6d, 0x20, 0x69, 0x6d, 0x61, 0x67, 0x65,  # "om image"
        0x21, 0x0a                                        # "!\n"
    ])
    
    return shellcode

def encode_code_to_image(code_bytes, output_path):
    """
    Encode machine code into a PNG image
    
    Each byte of code becomes one pixel value in the red channel.
    We use a simple encoding: R=code_byte, G=0, B=0
    """
    print("=" * 60)
    print("STEP 1: ENCODING MACHINE CODE INTO IMAGE")
    print("=" * 60)
    print()
    
    code_length = len(code_bytes)
    print(f"Code size: {code_length} bytes")
    print(f"Code (hex): {code_bytes.hex()}")
    print()
    
    # Calculate image dimensions (make it roughly square)
    width = int(code_length ** 0.5) + 1
    height = (code_length // width) + 1
    
    print(f"Image dimensions: {width}x{height} pixels")
    print()
    
    # Create image
    img = Image.new('RGB', (width, height), color=(0, 0, 0))
    pixels = img.load()
    
    # Encode code bytes into pixels
    for i, byte in enumerate(code_bytes):
        x = i % width
        y = i // width
        # Store byte in red channel, mark green channel with 255 to indicate valid data
        pixels[x, y] = (byte, 255, 0)
    
    # Save image
    img.save(output_path)
    print(f"✓ Code encoded into image: {output_path}")
    print(f"✓ Image saved successfully")
    print()
    
    return width, height, code_length

def decode_code_from_image(image_path, code_length):
    """
    Extract machine code from a PNG image
    
    Reads the red channel values and reconstructs the original code bytes.
    """
    print("=" * 60)
    print("STEP 2: EXTRACTING MACHINE CODE FROM IMAGE")
    print("=" * 60)
    print()
    
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size
    
    print(f"Image dimensions: {width}x{height} pixels")
    print()
    
    # Extract code bytes from pixels
    code_bytes = bytearray()
    for i in range(code_length):
        x = i % width
        y = i // width
        r, g, b = pixels[x, y]
        # Only extract if green channel is 255 (valid data marker)
        if g == 255:
            code_bytes.append(r)
    
    code_bytes = bytes(code_bytes)
    print(f"Extracted {len(code_bytes)} bytes")
    print(f"Code (hex): {code_bytes.hex()}")
    print()
    
    # Verify extraction
    if len(code_bytes) == code_length:
        print("✓ Extraction successful - byte count matches")
    else:
        print(f"✗ Extraction failed - expected {code_length} bytes, got {len(code_bytes)}")
    
    print()
    return code_bytes

def execute_code(code_bytes):
    """
    Execute the extracted machine code
    
    This is the dangerous/exciting part:
    1. Allocate executable memory
    2. Copy code into it
    3. Cast memory to a function pointer
    4. Call it!
    """
    print("=" * 60)
    print("STEP 3: EXECUTING CODE FROM IMAGE")
    print("=" * 60)
    print()
    
    print("⚠️  WARNING: About to execute code extracted from an image!")
    print()
    
    # Allocate executable memory
    # PROT_READ | PROT_WRITE | PROT_EXEC = 7
    code_size = len(code_bytes)
    
    # Create memory map with execute permissions
    mem = mmap.mmap(-1, code_size, 
                    prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC,
                    flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)
    
    # Write code to executable memory
    mem.write(code_bytes)
    mem.seek(0)
    
    print(f"✓ Allocated {code_size} bytes of executable memory")
    print(f"✓ Copied code into memory")
    print()
    
    # Get memory address
    mem_address = ctypes.addressof(ctypes.c_char.from_buffer(mem))
    print(f"Memory address: 0x{mem_address:x}")
    print()
    
    # Create function pointer
    # Function signature: void func(void)
    func_type = ctypes.CFUNCTYPE(None)
    func = func_type(mem_address)
    
    print("Executing code...")
    print("-" * 60)
    sys.stdout.flush()  # Flush before execution
    
    # EXECUTE THE IMAGE!
    try:
        func()
        sys.stdout.flush()  # Flush after execution
        print()
        print("-" * 60)
        print()
        print("✓ Code executed successfully!")
        print("✓ The message above was printed by code extracted from an image!")
        return True
    except Exception as e:
        print("-" * 60)
        print()
        print(f"✗ Execution failed: {e}")
        return False
    finally:
        mem.close()

def create_visual_proof():
    """
    Create a visual representation showing the code embedded in the image
    """
    print("=" * 60)
    print("STEP 4: CREATING VISUAL PROOF")
    print("=" * 60)
    print()
    
    # Load the image
    img_path = f"{EVIDENCE_DIR}/executable_code.png"
    img = Image.open(img_path)
    
    # Create a zoomed version to see the pixels
    zoomed = img.resize((img.width * 20, img.height * 20), Image.NEAREST)
    zoomed_path = f"{EVIDENCE_DIR}/executable_code_zoomed.png"
    zoomed.save(zoomed_path)
    
    print(f"✓ Created zoomed image: {zoomed_path}")
    print("  (Each pixel contains one byte of machine code)")
    print()

def main():
    print("\n" + "=" * 60)
    print("EXECUTABLE IMAGE EXPERIMENT")
    print("Can we run code extracted from a PNG image?")
    print("=" * 60)
    print()
    
    # Step 1: Create shellcode
    print("Creating x86-64 shellcode...")
    shellcode = create_hello_world_shellcode()
    print(f"✓ Shellcode created ({len(shellcode)} bytes)")
    print()
    
    # Step 2: Encode into image
    img_path = f"{EVIDENCE_DIR}/executable_code.png"
    width, height, code_length = encode_code_to_image(shellcode, img_path)
    
    # Step 3: Decode from image
    extracted_code = decode_code_from_image(img_path, code_length)
    
    # Verify extraction
    if extracted_code != shellcode:
        print("✗ FAILED: Extracted code doesn't match original!")
        print(f"Original:  {shellcode.hex()}")
        print(f"Extracted: {extracted_code.hex()}")
        return
    
    print("✓ VERIFIED: Extracted code matches original perfectly")
    print()
    
    # Step 4: Execute the code
    success = execute_code(extracted_code)
    
    # Step 5: Create visual proof
    create_visual_proof()
    
    # Final summary
    print("=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    print()
    
    if success:
        print("✓ VALIDATED: We successfully executed code from an image!")
        print()
        print("What this means:")
        print("  • Images can contain executable machine code")
        print("  • Pixel data can be interpreted as instructions")
        print("  • A PNG file literally RAN and printed text")
        print()
        print("Confidence: 🟢 CONFIRMED")
        print()
        print("This is possible because:")
        print("  1. Images are just bytes in memory")
        print("  2. CPUs don't care where code comes from")
        print("  3. With proper permissions, any bytes can execute")
        print()
        print("Real-world implications:")
        print("  • Novel steganography technique")
        print("  • Potential security vector (malicious images)")
        print("  • Code obfuscation method")
        print("  • Polyglot file format attacks")
    else:
        print("✗ FAILED: Could not execute code from image")
        print()
        print("Confidence: 🔴 UNVERIFIED")
    
    print()
    print("Evidence saved to:")
    print(f"  {EVIDENCE_DIR}/")
    print()
    print("Files:")
    print("  • executable_code.png - The image containing machine code")
    print("  • executable_code_zoomed.png - Zoomed view of pixels")
    print("=" * 60)

if __name__ == "__main__":
    # Check if we're on a compatible platform
    if sys.platform != "linux" or os.uname().machine != "x86_64":
        print("ERROR: This experiment requires Linux x86-64")
        sys.exit(1)
    
    main()
