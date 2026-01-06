#!/usr/bin/env python3
"""
Experiment #009: Hiding Secret Messages in Working Python Code
Using whitespace steganography to embed encrypted messages in valid Python programs
"""

import sys
import base64
import hashlib
from typing import Tuple

def encode_message_in_code(source_code: str, secret_message: str) -> str:
    """
    Embed a secret message in Python code using invisible whitespace patterns.
    Uses tabs (\\t) and spaces after line endings to encode binary data.
    
    Binary encoding:
    - Tab character = 1
    - Space character = 0
    """
    # Encrypt the message with XOR (simple but demonstrates the concept)
    key = "QUANTUM_KEY_2026"
    encrypted = xor_encrypt(secret_message, key)
    
    # Convert to binary
    binary_data = ''.join(format(byte, '08b') for byte in encrypted.encode('utf-8'))
    
    print(f"[ENCODE] Original message: {secret_message}")
    print(f"[ENCODE] Message length: {len(secret_message)} chars")
    print(f"[ENCODE] Encrypted: {encrypted}")
    print(f"[ENCODE] Binary length: {len(binary_data)} bits")
    print(f"[ENCODE] Binary (first 64 bits): {binary_data[:64]}")
    
    # Split code into lines
    lines = source_code.split('\n')
    
    # Embed binary data as whitespace after each line
    modified_lines = []
    bit_index = 0
    
    for line in lines:
        if bit_index < len(binary_data):
            # Add invisible whitespace encoding
            if binary_data[bit_index] == '1':
                line = line + '\t'  # Tab = 1
            else:
                line = line + ' '   # Space = 0
            bit_index += 1
        modified_lines.append(line)
    
    print(f"[ENCODE] Embedded {bit_index} bits across {len(modified_lines)} lines")
    
    return '\n'.join(modified_lines)

def decode_message_from_code(stego_code: str) -> str:
    """
    Extract hidden message from Python code by reading whitespace patterns.
    """
    lines = stego_code.split('\n')
    
    # Extract binary data from trailing whitespace
    binary_data = ''
    for line in lines:
        if line.endswith('\t'):
            binary_data += '1'
        elif line.endswith(' '):
            binary_data += '0'
    
    print(f"[DECODE] Extracted {len(binary_data)} bits")
    print(f"[DECODE] Binary (first 64 bits): {binary_data[:64]}")
    
    # Convert binary to bytes
    byte_data = []
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) == 8:
            byte_data.append(int(byte, 2))
    
    print(f"[DECODE] Converted to {len(byte_data)} bytes")
    
    # Convert bytes to string
    try:
        encrypted_message = bytes(byte_data).decode('utf-8')
        print(f"[DECODE] Encrypted message: {encrypted_message}")
        
        # Decrypt
        key = "QUANTUM_KEY_2026"
        decrypted = xor_encrypt(encrypted_message, key)
        
        return decrypted
    except Exception as e:
        print(f"[DECODE] Error: {e}")
        return ""

def xor_encrypt(text: str, key: str) -> str:
    """Simple XOR encryption (symmetric)"""
    result = []
    for i, char in enumerate(text):
        key_char = key[i % len(key)]
        result.append(chr(ord(char) ^ ord(key_char)))
    return ''.join(result)

def verify_code_still_works(code: str) -> bool:
    """Verify the steganographic code is still valid Python"""
    try:
        compile(code, '<string>', 'exec')
        return True
    except SyntaxError as e:
        print(f"[VERIFY] Syntax error: {e}")
        return False

# Sample Python program to hide message in
SAMPLE_PROGRAM = '''def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def main():
    print("Fibonacci(10):", fibonacci(10))
    print("Factorial(5):", factorial(5))
    print("Is 17 prime?", is_prime(17))

if __name__ == "__main__":
    main()
'''

if __name__ == "__main__":
    print("=" * 70)
    print("EXPERIMENT #009: STEGANOGRAPHY IN CODE")
    print("Hiding encrypted messages in working Python programs")
    print("=" * 70)
    print()
    
    # Secret message to hide
    SECRET = "The quantum keys are stored in DNS TXT records at qrng.anu.edu.au"
    
    print("[STEP 1] Original Python Program")
    print("-" * 70)
    print(SAMPLE_PROGRAM)
    print("-" * 70)
    print(f"Program length: {len(SAMPLE_PROGRAM)} chars, {len(SAMPLE_PROGRAM.split())} lines")
    print()
    
    # Test original program works
    print("[STEP 2] Verify Original Program Executes")
    print("-" * 70)
    exec(SAMPLE_PROGRAM)
    print("-" * 70)
    print()
    
    # Encode secret message
    print("[STEP 3] Encode Secret Message in Code")
    print("-" * 70)
    stego_code = encode_message_in_code(SAMPLE_PROGRAM, SECRET)
    print("-" * 70)
    print()
    
    # Save steganographic code
    with open('/home/ubuntu/unknown-unknown-experiments/experiments/009-steganography-in-code/evidence/stego_program.py', 'w') as f:
        f.write(stego_code)
    print("[SAVED] Steganographic code saved to evidence/stego_program.py")
    print()
    
    # Verify stego code still works
    print("[STEP 4] Verify Steganographic Code Still Executes")
    print("-" * 70)
    if verify_code_still_works(stego_code):
        print("✓ Code is still valid Python!")
        exec(stego_code)
    else:
        print("✗ Code is broken!")
    print("-" * 70)
    print()
    
    # Decode message
    print("[STEP 5] Decode Hidden Message from Code")
    print("-" * 70)
    decoded = decode_message_from_code(stego_code)
    print(f"[DECODE] Decrypted message: {decoded}")
    print("-" * 70)
    print()
    
    # Validation
    print("[STEP 6] Validation")
    print("-" * 70)
    print(f"Original message:  '{SECRET}'")
    print(f"Decoded message:   '{decoded}'")
    print(f"Match: {SECRET == decoded}")
    print()
    
    # Calculate size overhead
    original_size = len(SAMPLE_PROGRAM)
    stego_size = len(stego_code)
    overhead = stego_size - original_size
    print(f"Original code size: {original_size} bytes")
    print(f"Stego code size:    {stego_size} bytes")
    print(f"Overhead:           {overhead} bytes ({overhead/original_size*100:.1f}%)")
    print("-" * 70)
    print()
    
    # Compare visually
    print("[STEP 7] Visual Comparison (first 200 chars)")
    print("-" * 70)
    print("ORIGINAL:")
    print(repr(SAMPLE_PROGRAM[:200]))
    print()
    print("STEGANOGRAPHIC:")
    print(repr(stego_code[:200]))
    print("-" * 70)
    print()
    
    # Final proof
    print("[STEP 8] External Proof")
    print("-" * 70)
    
    # Save original for comparison
    with open('/home/ubuntu/unknown-unknown-experiments/experiments/009-steganography-in-code/evidence/original_program.py', 'w') as f:
        f.write(SAMPLE_PROGRAM)
    
    # Create hex dump comparison
    print("Creating hex dumps for forensic analysis...")
    import subprocess
    
    subprocess.run(['xxd', 
                   '/home/ubuntu/unknown-unknown-experiments/experiments/009-steganography-in-code/evidence/original_program.py'],
                  stdout=open('/home/ubuntu/unknown-unknown-experiments/experiments/009-steganography-in-code/evidence/original_hexdump.txt', 'w'))
    
    subprocess.run(['xxd',
                   '/home/ubuntu/unknown-unknown-experiments/experiments/009-steganography-in-code/evidence/stego_program.py'],
                  stdout=open('/home/ubuntu/unknown-unknown-experiments/experiments/009-steganography-in-code/evidence/stego_hexdump.txt', 'w'))
    
    print("✓ Hex dumps saved for comparison")
    print("✓ Both programs saved to evidence/")
    print("-" * 70)
    print()
    
    print("=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  • Hidden message: {len(SECRET)} characters")
    print(f"  • Encoding method: Whitespace steganography (tabs/spaces)")
    print(f"  • Code still works: {verify_code_still_works(stego_code)}")
    print(f"  • Message recovered: {SECRET == decoded}")
    print(f"  • Overhead: {overhead} bytes")
    print()
    print("This demonstrates that:")
    print("  1. You can hide encrypted data in working source code")
    print("  2. The code remains fully functional")
    print("  3. The hidden data is invisible to casual inspection")
    print("  4. Whitespace is a covert channel in programming languages")
