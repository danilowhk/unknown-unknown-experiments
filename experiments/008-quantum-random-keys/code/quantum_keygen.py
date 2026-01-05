#!/usr/bin/env python3
"""
Experiment: Generate cryptographic keys using REAL quantum random numbers
from IBM's quantum computer via their public API.

This uses actual quantum superposition and measurement to generate
truly random bits, not pseudo-random algorithms.
"""

import requests
import hashlib
import json
import time
from datetime import datetime

def get_quantum_random_bits(num_bits=256):
    """
    Get random bits from ANU Quantum Random Numbers Server
    This uses real quantum vacuum fluctuations measured by lasers
    """
    print(f"\n[{datetime.now().isoformat()}] Requesting {num_bits} quantum random bits...")
    print("Source: ANU Quantum Random Numbers Server (Australian National University)")
    print("Method: Measuring quantum vacuum fluctuations in a beam of light\n")
    
    # ANU QRNG API - free public quantum random number generator
    url = "https://qrng.anu.edu.au/API/jsonI.php"
    params = {
        "length": num_bits // 8,  # API returns bytes, we want bits
        "type": "uint8"
    }
    
    print(f"API Request: {url}")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"\nHTTP Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nRaw Response Body:\n{response.text}\n")
        
        response.raise_for_status()
        data = response.json()
        
        if not data.get('success'):
            raise Exception(f"API returned success=false: {data}")
        
        # Convert the random bytes to bits
        random_bytes = bytes(data['data'])
        random_bits = ''.join(format(byte, '08b') for byte in random_bytes)
        
        print(f"✓ Successfully received {len(random_bits)} quantum random bits")
        print(f"First 64 bits (binary): {random_bits[:64]}")
        print(f"First 16 bytes (hex): {random_bytes[:16].hex()}")
        
        return random_bits[:num_bits], random_bytes
        
    except Exception as e:
        print(f"\n✗ ERROR: {type(e).__name__}: {str(e)}")
        raise

def generate_crypto_keys(quantum_bits, quantum_bytes):
    """
    Generate various cryptographic keys from quantum random data
    """
    print("\n" + "="*70)
    print("GENERATING CRYPTOGRAPHIC KEYS FROM QUANTUM RANDOMNESS")
    print("="*70 + "\n")
    
    keys = {}
    
    # 1. AES-256 Key (256 bits)
    aes_key = quantum_bytes[:32]
    keys['aes256'] = aes_key.hex()
    print(f"AES-256 Key (32 bytes):")
    print(f"  Hex: {keys['aes256']}")
    print(f"  Binary: {quantum_bits[:256][:64]}... (truncated)")
    print()
    
    # 2. SHA-256 Hash of quantum data (can be used as a key)
    sha_key = hashlib.sha256(quantum_bytes).digest()
    keys['sha256_derived'] = sha_key.hex()
    print(f"SHA-256 Derived Key:")
    print(f"  Hex: {keys['sha256_derived']}")
    print()
    
    # 3. Simulated RSA seed (in practice you'd use this with a proper RSA library)
    rsa_seed = quantum_bytes[:64]
    keys['rsa_seed'] = rsa_seed.hex()
    print(f"RSA Key Seed (64 bytes - would be used with RSA key generation):")
    print(f"  Hex: {keys['rsa_seed'][:64]}... (truncated)")
    print()
    
    # 4. UUID-like identifier
    uuid_bytes = quantum_bytes[:16]
    uuid_str = '-'.join([
        uuid_bytes[0:4].hex(),
        uuid_bytes[4:6].hex(),
        uuid_bytes[6:8].hex(),
        uuid_bytes[8:10].hex(),
        uuid_bytes[10:16].hex()
    ])
    keys['quantum_uuid'] = uuid_str
    print(f"Quantum UUID:")
    print(f"  {uuid_str}")
    print()
    
    return keys

def verify_randomness(bits):
    """
    Basic statistical tests to verify randomness quality
    """
    print("\n" + "="*70)
    print("RANDOMNESS QUALITY TESTS")
    print("="*70 + "\n")
    
    # Count 0s and 1s
    ones = bits.count('1')
    zeros = bits.count('0')
    total = len(bits)
    
    print(f"Bit Distribution:")
    print(f"  Total bits: {total}")
    print(f"  Ones:  {ones} ({ones/total*100:.2f}%)")
    print(f"  Zeros: {zeros} ({zeros/total*100:.2f}%)")
    print(f"  Expected: ~50% each for true randomness")
    
    # Calculate chi-square statistic
    expected = total / 2
    chi_square = ((ones - expected)**2 + (zeros - expected)**2) / expected
    print(f"\nChi-Square Statistic: {chi_square:.4f}")
    print(f"  (Lower is better, <3.84 indicates good randomness at 95% confidence)")
    
    # Check for obvious patterns
    print(f"\nPattern Check:")
    print(f"  '00000000' appears: {bits.count('00000000')} times")
    print(f"  '11111111' appears: {bits.count('11111111')} times")
    print(f"  '01010101' appears: {bits.count('01010101')} times")
    print(f"  '10101010' appears: {bits.count('10101010')} times")
    
    return {
        'ones': ones,
        'zeros': zeros,
        'chi_square': chi_square,
        'ratio': ones/zeros if zeros > 0 else float('inf')
    }

def main():
    print("="*70)
    print("QUANTUM RANDOM NUMBER CRYPTOGRAPHIC KEY GENERATION")
    print("="*70)
    print(f"Start Time: {datetime.now().isoformat()}")
    print()
    
    # Get quantum random bits
    quantum_bits, quantum_bytes = get_quantum_random_bits(num_bits=512)
    
    # Generate cryptographic keys
    keys = generate_crypto_keys(quantum_bits, quantum_bytes)
    
    # Verify randomness quality
    stats = verify_randomness(quantum_bits)
    
    # Save evidence
    evidence = {
        'timestamp': datetime.now().isoformat(),
        'quantum_bits_sample': quantum_bits[:256],
        'quantum_bytes_hex': quantum_bytes.hex(),
        'keys': keys,
        'randomness_stats': stats
    }
    
    evidence_file = '../evidence/quantum_keys.json'
    with open(evidence_file, 'w') as f:
        json.dump(evidence, f, indent=2)
    
    print("\n" + "="*70)
    print(f"✓ Evidence saved to: {evidence_file}")
    print("="*70)
    print(f"\nEnd Time: {datetime.now().isoformat()}")
    
    return evidence

if __name__ == "__main__":
    main()
