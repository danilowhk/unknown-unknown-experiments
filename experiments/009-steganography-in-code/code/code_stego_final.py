#!/usr/bin/env python3
"""
Experiment #009: Hiding Secret Messages in Working Python Code (FINAL)
Using whitespace steganography - message sized to fit available capacity
"""

import sys
import base64

def encode_message_in_code(source_code: str, secret_message: str) -> str:
    """
    Embed a secret message in Python code using invisible whitespace patterns.
    Uses multiple spaces/tabs at the end of each line to encode multiple bits.
    
    Encoding scheme (per line):
    - Each line can encode multiple bits using a sequence of spaces and tabs
    - We use groups of 2 whitespace characters to encode 2 bits:
      "  " (2 spaces) = 00
      " \\t" (space+tab) = 01
      "\\t " (tab+space) = 10
      "\\t\\t" (2 tabs) = 11
    """
    # Encrypt the message with XOR
    key = "QUANTUM"
    encrypted = xor_encrypt(secret_message, key)
    
    # Convert to binary
    binary_data = ''.join(format(ord(char), '08b') for char in encrypted)
    
    print(f"[ENCODE] Original message: {secret_message}")
    print(f"[ENCODE] Message length: {len(secret_message)} chars")
    print(f"[ENCODE] Encrypted: {repr(encrypted)}")
    print(f"[ENCODE] Binary length: {len(binary_data)} bits")
    print(f"[ENCODE] Binary (first 64 bits): {binary_data[:64]}")
    
    # Split code into lines
    lines = source_code.split('\n')
    
    # Calculate bits per line
    bits_per_line = 8  # 4 groups of 2 bits each
    
    print(f"[ENCODE] Available lines: {len(lines)}")
    print(f"[ENCODE] Bits per line: {bits_per_line}")
    print(f"[ENCODE] Total capacity: {len(lines) * bits_per_line} bits ({len(lines) * bits_per_line // 8} bytes)")
    print(f"[ENCODE] Required capacity: {len(binary_data)} bits ({len(binary_data) // 8} bytes)")
    
    if len(binary_data) > len(lines) * bits_per_line:
        print(f"[ENCODE] WARNING: Message too long! Truncating to fit.")
        binary_data = binary_data[:len(lines) * bits_per_line]
    
    # Embed binary data as whitespace after each line
    modified_lines = []
    bit_index = 0
    
    for line in lines:
        # Encode up to 8 bits per line using 4 groups of 2-char whitespace
        whitespace = ""
        for _ in range(4):  # 4 groups of 2 bits each
            if bit_index + 1 < len(binary_data):
                two_bits = binary_data[bit_index:bit_index+2]
                if two_bits == '00':
                    whitespace += '  '  # 2 spaces
                elif two_bits == '01':
                    whitespace += ' \t'  # space + tab
                elif two_bits == '10':
                    whitespace += '\t '  # tab + space
                elif two_bits == '11':
                    whitespace += '\t\t'  # 2 tabs
                bit_index += 2
            elif bit_index < len(binary_data):
                # Last bit - pad with 0
                one_bit = binary_data[bit_index]
                if one_bit == '0':
                    whitespace += '  '
                else:
                    whitespace += ' \t'
                bit_index += 1
                break
        
        modified_lines.append(line + whitespace)
    
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
        # Find trailing whitespace
        stripped = line.rstrip('\t ')
        trailing = line[len(stripped):]
        
        # Decode in groups of 2 characters
        i = 0
        while i + 1 < len(trailing):
            two_chars = trailing[i:i+2]
            if two_chars == '  ':
                binary_data += '00'
            elif two_chars == ' \t':
                binary_data += '01'
            elif two_chars == '\t ':
                binary_data += '10'
            elif two_chars == '\t\t':
                binary_data += '11'
            i += 2
        
        # Handle single trailing character if any
        if i < len(trailing):
            if trailing[i] == ' ':
                binary_data += '0'
            else:
                binary_data += '1'
    
    print(f"[DECODE] Extracted {len(binary_data)} bits")
    print(f"[DECODE] Binary (first 64 bits): {binary_data[:64]}")
    
    # Convert binary to characters
    chars = []
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))
    
    encrypted_message = ''.join(chars)
    print(f"[DECODE] Encrypted message: {repr(encrypted_message)}")
    
    try:
        # Decrypt
        key = "QUANTUM"
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
    print("EXPERIMENT #009: STEGANOGRAPHY IN CODE (FINAL)")
    print("Hiding encrypted messages in working Python programs")
    print("=" * 70)
    print()
    
    # Secret message to hide - sized to fit 26 lines * 8 bits = 208 bits = 26 bytes
    SECRET = "QUANTUM_KEYS_AT_ANU_EDU_AU"  # Exactly 26 characters
    
    print("[STEP 1] Original Python Program")
    print("-" * 70)
    print(SAMPLE_PROGRAM)
    print("-" * 70)
    print(f"Program length: {len(SAMPLE_PROGRAM)} chars, {len(SAMPLE_PROGRAM.splitlines())} lines")
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
    with open('/home/ubuntu/unknown-unknown-experiments/experiments/009-steganography-in-code/evidence/stego_program_final.py', 'w') as f:
        f.write(stego_code)
    print("[SAVED] Steganographic code saved to evidence/stego_program_final.py")
    print()
    
    # Verify stego code still works
    print("[STEP 4] Verify Steganographic Code Still Executes")
    print("-" * 70)
    if verify_code_still_works(stego_code):
        print("✓ Code is still valid Python!")
        print("\nExecuting steganographic code:")
        exec(stego_code)
    else:
        print("✗ Code is broken!")
    print("-" * 70)
    print()
    
    # Decode message
    print("[STEP 5] Decode Hidden Message from Code")
    print("-" * 70)
    decoded = decode_message_from_code(stego_code)
    print(f"[DECODE] Decrypted message: {repr(decoded)}")
    print("-" * 70)
    print()
    
    # Validation
    print("[STEP 6] Validation")
    print("-" * 70)
    print(f"Original message:  '{SECRET}'")
    print(f"Decoded message:   '{decoded}'")
    print(f"Match: {SECRET == decoded}")
    
    if SECRET == decoded:
        print("\n✓✓✓ SUCCESS! Message perfectly recovered! ✓✓✓")
    else:
        print(f"\n✗ MISMATCH")
        print(f"  Expected length: {len(SECRET)}")
        print(f"  Got length: {len(decoded)}")
    
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
    print("[STEP 7] Visual Comparison")
    print("-" * 70)
    print("ORIGINAL (first 150 chars):")
    print(repr(SAMPLE_PROGRAM[:150]))
    print()
    print("STEGANOGRAPHIC (first 150 chars):")
    print(repr(stego_code[:150]))
    print()
    print("Notice: The stego version has invisible tabs and spaces at line ends!")
    print("-" * 70)
    print()
    
    # Show hex comparison of first line
    print("[STEP 8] Forensic Analysis - Hex Comparison")
    print("-" * 70)
    orig_first_line = SAMPLE_PROGRAM.split('\n')[0]
    stego_first_line = stego_code.split('\n')[0]
    
    print(f"Original first line: {repr(orig_first_line)}")
    print(f"Hex: {orig_first_line.encode().hex()}")
    print()
    print(f"Stego first line: {repr(stego_first_line)}")
    print(f"Hex: {stego_first_line.encode().hex()}")
    print()
    print("The difference is in the trailing whitespace (invisible to humans)")
    print("-" * 70)
    print()
    
    # Final proof
    print("[STEP 9] External Proof")
    print("-" * 70)
    
    # Save both versions
    with open('/home/ubuntu/unknown-unknown-experiments/experiments/009-steganography-in-code/evidence/original_final.py', 'w') as f:
        f.write(SAMPLE_PROGRAM)
    
    # Test that stego code actually executes
    print("Testing steganographic code execution...")
    import subprocess
    result = subprocess.run(['python3', '/home/ubuntu/unknown-unknown-experiments/experiments/009-steganography-in-code/evidence/stego_program_final.py'],
                          capture_output=True, text=True)
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    print(f"Exit code: {result.returncode}")
    
    print("\n✓ Both programs saved to evidence/")
    print("-" * 70)
    print()
    
    print("=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
    print()
    print("RESULTS:")
    print(f"  ✓ Hidden message: {len(SECRET)} characters")
    print(f"  ✓ Encoding method: Multi-bit whitespace steganography")
    print(f"  ✓ Code still compiles: {verify_code_still_works(stego_code)}")
    print(f"  ✓ Code still executes: {result.returncode == 0}")
    print(f"  ✓ Message recovered: {SECRET == decoded}")
    print(f"  ✓ Overhead: {overhead} bytes ({overhead/original_size*100:.1f}%)")
    print()
    print("WHAT THIS PROVES:")
    print("  1. You can hide encrypted data in working source code")
    print("  2. The code remains fully functional after modification")
    print("  3. The hidden data is invisible to human code review")
    print("  4. Whitespace is a covert channel in programming languages")
    print("  5. Standard code review won't detect this")
    print("  6. You need forensic tools (hex dumps) to find it")
    print()
    print("SECURITY IMPLICATIONS:")
    print("  • Malicious code could hide payloads in legitimate programs")
    print("  • Data exfiltration through code commits")
    print("  • Covert communication via open-source repositories")
    print("  • Supply chain attacks hiding in plain sight")
