#!/usr/bin/env python3
"""
Experiment: Generate cryptographic keys using REAL quantum random numbers
Attempt 2: Try multiple quantum sources and handle SSL issues
"""

import requests
import hashlib
import json
import time
from datetime import datetime
import urllib3

# Disable SSL warnings for expired certs (we'll document this!)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_quantum_random_anu(num_bits=256):
    """
    Attempt 1: ANU Quantum Random Numbers Server
    Uses quantum vacuum fluctuations measured by lasers
    """
    print(f"\n[ATTEMPT 1: ANU QRNG]")
    print(f"[{datetime.now().isoformat()}] Requesting {num_bits} quantum random bits...")
    print("Source: ANU Quantum Random Numbers Server (Australian National University)")
    print("Method: Measuring quantum vacuum fluctuations in a beam of light\n")
    
    url = "https://qrng.anu.edu.au/API/jsonI.php"
    params = {
        "length": num_bits // 8,
        "type": "uint8"
    }
    
    print(f"API Request: {url}")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    
    try:
        # Try with SSL verification disabled due to expired cert
        response = requests.get(url, params=params, timeout=30, verify=False)
        print(f"\nHTTP Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nRaw Response Body:\n{response.text}\n")
        
        response.raise_for_status()
        data = response.json()
        
        if not data.get('success'):
            raise Exception(f"API returned success=false: {data}")
        
        random_bytes = bytes(data['data'])
        random_bits = ''.join(format(byte, '08b') for byte in random_bytes)
        
        print(f"✓ SUCCESS! Received {len(random_bits)} quantum random bits from ANU")
        print(f"First 64 bits (binary): {random_bits[:64]}")
        print(f"First 16 bytes (hex): {random_bytes[:16].hex()}")
        
        return random_bits[:num_bits], random_bytes, "ANU_QRNG"
        
    except Exception as e:
        print(f"\n✗ FAILED: {type(e).__name__}: {str(e)}")
        return None, None, None

def get_quantum_random_qrandom(num_bits=256):
    """
    Attempt 2: QRANDOM.net - Another quantum random number service
    """
    print(f"\n[ATTEMPT 2: QRANDOM.net]")
    print(f"[{datetime.now().isoformat()}] Requesting {num_bits} quantum random bits...")
    print("Source: QRANDOM.net")
    print("Method: Quantum random number generation\n")
    
    num_bytes = num_bits // 8
    url = f"https://qrandom.net/api/v1/random/bytes/{num_bytes}"
    
    print(f"API Request: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"\nHTTP Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nRaw Response Body:\n{response.text}\n")
        
        response.raise_for_status()
        data = response.json()
        
        if not data.get('success'):
            raise Exception(f"API returned success=false: {data}")
        
        # The API returns base64 encoded data
        import base64
        random_bytes = base64.b64decode(data['data'])
        random_bits = ''.join(format(byte, '08b') for byte in random_bytes)
        
        print(f"✓ SUCCESS! Received {len(random_bits)} quantum random bits from QRANDOM")
        print(f"First 64 bits (binary): {random_bits[:64]}")
        print(f"First 16 bytes (hex): {random_bytes[:16].hex()}")
        
        return random_bits[:num_bits], random_bytes, "QRANDOM"
        
    except Exception as e:
        print(f"\n✗ FAILED: {type(e).__name__}: {str(e)}")
        return None, None, None

def get_quantum_random_randomorg(num_bits=256):
    """
    Attempt 3: Random.org - Uses atmospheric noise (not quantum, but true random)
    Fallback option to show contrast with quantum sources
    """
    print(f"\n[ATTEMPT 3: Random.org (Atmospheric Noise - NOT quantum)]")
    print(f"[{datetime.now().isoformat()}] Requesting {num_bits} random bits...")
    print("Source: Random.org")
    print("Method: Atmospheric noise (radio receivers)\n")
    
    num_bytes = num_bits // 8
    url = "https://www.random.org/cgi-bin/randbyte"
    params = {
        "nbytes": num_bytes,
        "format": "h"  # hex format
    }
    
    print(f"API Request: {url}")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"\nHTTP Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nRaw Response Body:\n{response.text}\n")
        
        response.raise_for_status()
        
        # Parse hex response
        hex_data = response.text.strip().replace('\n', '').replace('\t', '').replace(' ', '')
        random_bytes = bytes.fromhex(hex_data)
        random_bits = ''.join(format(byte, '08b') for byte in random_bytes)
        
        print(f"✓ SUCCESS! Received {len(random_bits)} atmospheric random bits from Random.org")
        print(f"First 64 bits (binary): {random_bits[:64]}")
        print(f"First 16 bytes (hex): {random_bytes[:16].hex()}")
        
        return random_bits[:num_bits], random_bytes, "RANDOM_ORG_ATMOSPHERIC"
        
    except Exception as e:
        print(f"\n✗ FAILED: {type(e).__name__}: {str(e)}")
        return None, None, None

def generate_crypto_keys(quantum_bits, quantum_bytes, source):
    """
    Generate various cryptographic keys from quantum random data
    """
    print("\n" + "="*70)
    print(f"GENERATING CRYPTOGRAPHIC KEYS FROM {source}")
    print("="*70 + "\n")
    
    keys = {}
    
    # 1. AES-256 Key (256 bits)
    aes_key = quantum_bytes[:32]
    keys['aes256'] = aes_key.hex()
    print(f"AES-256 Key (32 bytes):")
    print(f"  Hex: {keys['aes256']}")
    print(f"  Binary: {quantum_bits[:256][:64]}... (truncated)")
    print()
    
    # 2. SHA-256 Hash of quantum data
    sha_key = hashlib.sha256(quantum_bytes).digest()
    keys['sha256_derived'] = sha_key.hex()
    print(f"SHA-256 Derived Key:")
    print(f"  Hex: {keys['sha256_derived']}")
    print()
    
    # 3. RSA seed
    rsa_seed = quantum_bytes[:64] if len(quantum_bytes) >= 64 else quantum_bytes
    keys['rsa_seed'] = rsa_seed.hex()
    print(f"RSA Key Seed ({len(rsa_seed)} bytes):")
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

def verify_randomness(bits, source):
    """
    Basic statistical tests to verify randomness quality
    """
    print("\n" + "="*70)
    print(f"RANDOMNESS QUALITY TESTS - {source}")
    print("="*70 + "\n")
    
    ones = bits.count('1')
    zeros = bits.count('0')
    total = len(bits)
    
    print(f"Bit Distribution:")
    print(f"  Total bits: {total}")
    print(f"  Ones:  {ones} ({ones/total*100:.2f}%)")
    print(f"  Zeros: {zeros} ({zeros/total*100:.2f}%)")
    print(f"  Expected: ~50% each for true randomness")
    
    expected = total / 2
    chi_square = ((ones - expected)**2 + (zeros - expected)**2) / expected
    print(f"\nChi-Square Statistic: {chi_square:.4f}")
    print(f"  (Lower is better, <3.84 indicates good randomness at 95% confidence)")
    
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
    
    # Try multiple sources
    sources = [
        get_quantum_random_anu,
        get_quantum_random_qrandom,
        get_quantum_random_randomorg
    ]
    
    quantum_bits = None
    quantum_bytes = None
    source_name = None
    
    for source_func in sources:
        bits, bytes_data, name = source_func(num_bits=512)
        if bits is not None:
            quantum_bits = bits
            quantum_bytes = bytes_data
            source_name = name
            break
    
    if quantum_bits is None:
        print("\n" + "="*70)
        print("✗ ALL SOURCES FAILED - Cannot complete experiment")
        print("="*70)
        return None
    
    # Generate cryptographic keys
    keys = generate_crypto_keys(quantum_bits, quantum_bytes, source_name)
    
    # Verify randomness quality
    stats = verify_randomness(quantum_bits, source_name)
    
    # Save evidence
    evidence = {
        'timestamp': datetime.now().isoformat(),
        'source': source_name,
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
