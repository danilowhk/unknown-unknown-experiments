#!/usr/bin/env python3
"""
Experiment: Can we execute Python code that's encoded in audio waveforms?

This tests whether we can:
1. Encode Python bytecode into audio samples
2. Save it as a WAV file (actual audio)
3. Extract the bytecode back from the audio
4. Execute it as Python code

This is a "wait, THAT'S possible?!" moment because audio files are meant
for sound, but here we're treating audio samples as executable bytecode.
"""

import os
import sys
import wave
import struct
import types
import marshal
import dis

# Evidence directory
EVIDENCE_DIR = "/home/ubuntu/unknown-unknown-experiments/experiments/005-audio-executable/evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def create_test_function():
    """
    Create a Python function that we'll encode into audio.
    
    We'll use something that produces verifiable output so we know
    it actually executed and isn't just a hallucination.
    """
    print("=" * 60)
    print("STEP 1: CREATING PYTHON FUNCTION TO ENCODE")
    print("=" * 60)
    print()
    
    # Define a function that does something interesting
    def audio_function():
        """This function was encoded in audio and executed!"""
        import time
        timestamp = time.time()
        message = f"🎵 Hello from audio waveform! Executed at {timestamp}"
        return message
    
    # Show the function
    print("Function definition:")
    print("-" * 60)
    print("def audio_function():")
    print('    """This function was encoded in audio and executed!"""')
    print("    import time")
    print("    timestamp = time.time()")
    print('    message = f"🎵 Hello from audio waveform! Executed at {timestamp}"')
    print("    return message")
    print("-" * 60)
    print()
    
    # Get the bytecode
    code_object = audio_function.__code__
    bytecode = marshal.dumps(code_object)
    
    print(f"Function bytecode size: {len(bytecode)} bytes")
    print(f"Bytecode (first 50 bytes hex): {bytecode[:50].hex()}")
    print()
    
    # Show disassembly for proof
    print("Bytecode disassembly (human-readable):")
    print("-" * 60)
    dis.dis(audio_function)
    print("-" * 60)
    print()
    
    return bytecode, audio_function

def encode_bytecode_to_audio(bytecode, output_path):
    """
    Encode Python bytecode into audio samples.
    
    Each byte becomes an audio sample. We'll use 8-bit audio
    where each sample value IS the bytecode byte.
    """
    print("=" * 60)
    print("STEP 2: ENCODING BYTECODE INTO AUDIO")
    print("=" * 60)
    print()
    
    print(f"Input: {len(bytecode)} bytes of Python bytecode")
    print()
    
    # Audio parameters
    sample_rate = 44100  # Standard CD quality
    channels = 1  # Mono
    sample_width = 1  # 8-bit audio (1 byte per sample)
    
    print(f"Audio format:")
    print(f"  Sample rate: {sample_rate} Hz")
    print(f"  Channels: {channels} (mono)")
    print(f"  Sample width: {sample_width} byte (8-bit)")
    print(f"  Duration: {len(bytecode) / sample_rate:.4f} seconds")
    print()
    
    # Create WAV file
    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        
        # Write bytecode as audio samples
        # Each byte becomes one audio sample
        wav_file.writeframes(bytecode)
    
    file_size = os.path.getsize(output_path)
    print(f"✓ Audio file created: {output_path}")
    print(f"✓ File size: {file_size} bytes")
    print()
    
    # Verify file
    with wave.open(output_path, 'rb') as wav_file:
        params = wav_file.getparams()
        print("Verification - WAV file parameters:")
        print(f"  Channels: {params.nchannels}")
        print(f"  Sample width: {params.sampwidth} bytes")
        print(f"  Frame rate: {params.framerate} Hz")
        print(f"  Number of frames: {params.nframes}")
        print(f"  Compression: {params.comptype}")
    print()
    
    return output_path

def decode_bytecode_from_audio(audio_path):
    """
    Extract Python bytecode from audio samples.
    
    Read the audio samples and reconstruct the original bytecode.
    """
    print("=" * 60)
    print("STEP 3: EXTRACTING BYTECODE FROM AUDIO")
    print("=" * 60)
    print()
    
    print(f"Reading audio file: {audio_path}")
    print()
    
    # Open WAV file
    with wave.open(audio_path, 'rb') as wav_file:
        params = wav_file.getparams()
        print(f"Audio parameters:")
        print(f"  Sample rate: {params.framerate} Hz")
        print(f"  Channels: {params.nchannels}")
        print(f"  Sample width: {params.sampwidth} bytes")
        print(f"  Frame count: {params.nframes}")
        print()
        
        # Read all frames (samples)
        frames = wav_file.readframes(params.nframes)
    
    # The frames ARE the bytecode
    extracted_bytecode = frames
    
    print(f"Extracted {len(extracted_bytecode)} bytes")
    print(f"Bytecode (first 50 bytes hex): {extracted_bytecode[:50].hex()}")
    print()
    
    return extracted_bytecode

def execute_bytecode(bytecode):
    """
    Execute Python bytecode that was extracted from audio.
    
    This is the dangerous/exciting part:
    1. Unmarshal the bytecode into a code object
    2. Create a function from the code object
    3. Execute it!
    """
    print("=" * 60)
    print("STEP 4: EXECUTING CODE FROM AUDIO")
    print("=" * 60)
    print()
    
    print("⚠️  WARNING: About to execute code extracted from an audio file!")
    print()
    
    try:
        # Unmarshal bytecode back to code object
        code_object = marshal.loads(bytecode)
        print("✓ Successfully unmarshaled bytecode to code object")
        print()
        
        # Show code object details
        print("Code object details:")
        print(f"  Name: {code_object.co_name}")
        print(f"  Argument count: {code_object.co_argcount}")
        print(f"  Local variables: {code_object.co_nlocals}")
        print(f"  Stack size: {code_object.co_stacksize}")
        print(f"  Constants: {code_object.co_consts}")
        print()
        
        # Create function from code object
        func = types.FunctionType(code_object, globals())
        print("✓ Created function from code object")
        print()
        
        # Execute the function!
        print("Executing function extracted from audio...")
        print("-" * 60)
        sys.stdout.flush()
        
        result = func()
        
        print(result)
        print("-" * 60)
        print()
        
        print("✓ Function executed successfully!")
        print(f"✓ Return value: {result}")
        print()
        
        # Save result to file as proof
        result_file = f"{EVIDENCE_DIR}/execution_result.txt"
        with open(result_file, 'w') as f:
            f.write(f"Execution Result\n")
            f.write(f"================\n\n")
            f.write(f"Return value: {result}\n\n")
            f.write(f"This output was generated by executing Python bytecode\n")
            f.write(f"that was encoded in an audio file's waveform data.\n")
        
        print(f"✓ Result saved to: {result_file}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"✗ Execution failed: {type(e).__name__}: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False, None

def create_visual_proof(audio_path, bytecode):
    """
    Create visualizations and additional proof files.
    """
    print("=" * 60)
    print("STEP 5: CREATING VISUAL PROOF")
    print("=" * 60)
    print()
    
    # Create a text file showing the bytecode
    bytecode_file = f"{EVIDENCE_DIR}/bytecode_hex.txt"
    with open(bytecode_file, 'w') as f:
        f.write("Python Bytecode (Hexadecimal)\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Size: {len(bytecode)} bytes\n\n")
        
        # Write hex dump
        for i in range(0, len(bytecode), 16):
            chunk = bytecode[i:i+16]
            hex_str = ' '.join(f'{b:02x}' for b in chunk)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            f.write(f"{i:08x}  {hex_str:<48}  {ascii_str}\n")
    
    print(f"✓ Created bytecode hex dump: {bytecode_file}")
    
    # Create audio info file
    audio_info_file = f"{EVIDENCE_DIR}/audio_info.txt"
    with wave.open(audio_path, 'rb') as wav_file:
        params = wav_file.getparams()
        with open(audio_info_file, 'w') as f:
            f.write("Audio File Information\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"File: {audio_path}\n")
            f.write(f"Size: {os.path.getsize(audio_path)} bytes\n\n")
            f.write(f"WAV Parameters:\n")
            f.write(f"  Channels: {params.nchannels}\n")
            f.write(f"  Sample width: {params.sampwidth} bytes\n")
            f.write(f"  Frame rate: {params.framerate} Hz\n")
            f.write(f"  Number of frames: {params.nframes}\n")
            f.write(f"  Duration: {params.nframes / params.framerate:.4f} seconds\n")
            f.write(f"\nThis audio file contains executable Python bytecode!\n")
    
    print(f"✓ Created audio info file: {audio_info_file}")
    print()

def main():
    print("\n" + "=" * 60)
    print("AUDIO EXECUTABLE EXPERIMENT")
    print("Can we execute Python code encoded in audio waveforms?")
    print("=" * 60)
    print()
    
    # Step 1: Create function and get bytecode
    bytecode, original_func = create_test_function()
    
    # Execute original function for comparison
    print("Executing ORIGINAL function (for comparison):")
    print("-" * 60)
    original_result = original_func()
    print(original_result)
    print("-" * 60)
    print()
    
    # Step 2: Encode into audio
    audio_path = f"{EVIDENCE_DIR}/executable_code.wav"
    encode_bytecode_to_audio(bytecode, audio_path)
    
    # Step 3: Decode from audio
    extracted_bytecode = decode_bytecode_from_audio(audio_path)
    
    # Verify extraction
    print("=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    print()
    
    if extracted_bytecode == bytecode:
        print("✓ VERIFIED: Extracted bytecode matches original perfectly!")
        print(f"  Original size: {len(bytecode)} bytes")
        print(f"  Extracted size: {len(extracted_bytecode)} bytes")
        print(f"  Byte-for-byte match: YES")
    else:
        print("✗ FAILED: Extracted bytecode doesn't match original!")
        print(f"  Original size: {len(bytecode)} bytes")
        print(f"  Extracted size: {len(extracted_bytecode)} bytes")
        return
    print()
    
    # Step 4: Execute the extracted bytecode
    success, result = execute_bytecode(extracted_bytecode)
    
    # Step 5: Create visual proof
    if success:
        create_visual_proof(audio_path, bytecode)
    
    # Final summary
    print("=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    print()
    
    if success:
        print("✓ VALIDATED: We successfully executed code from an audio file!")
        print()
        print("What this means:")
        print("  • Audio files can contain executable Python bytecode")
        print("  • Waveform data can be interpreted as code")
        print("  • A WAV file literally RAN and returned a value")
        print("  • The audio would sound like noise if played")
        print()
        print("Confidence: 🟢 CONFIRMED")
        print()
        print("This is possible because:")
        print("  1. Audio samples are just bytes in memory")
        print("  2. Python bytecode is also just bytes")
        print("  3. marshal can reconstruct code objects from bytes")
        print("  4. Functions can be created from code objects")
        print()
        print("Real-world implications:")
        print("  • Novel steganography technique")
        print("  • Code can be hidden in audio files")
        print("  • Potential security vector (malicious audio)")
        print("  • Polyglot file format attacks")
        print("  • Audio-based code distribution")
        print()
        print("Key difference from image experiment:")
        print("  • Images used machine code (x86 assembly)")
        print("  • This uses Python bytecode (higher level)")
        print("  • Both prove: any file format can carry executable code")
    else:
        print("✗ FAILED: Could not execute code from audio")
        print()
        print("Confidence: 🔴 UNVERIFIED")
    
    print()
    print("Evidence saved to:")
    print(f"  {EVIDENCE_DIR}/")
    print()
    print("Files:")
    print("  • executable_code.wav - Audio file containing Python bytecode")
    print("  • execution_result.txt - Output from executed code")
    print("  • bytecode_hex.txt - Hex dump of the bytecode")
    print("  • audio_info.txt - Audio file metadata")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
