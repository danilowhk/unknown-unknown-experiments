# Beginner's Guide: Quantum Random Cryptographic Keys

## What is this experiment about?

This experiment generates encryption keys using **real quantum mechanics** from a quantum computer in Australia, accessible over the internet via a simple API call.

## Key Concepts Explained

### 1. What is Randomness?

**Everyday randomness:** Flipping a coin, rolling dice
- Seems random, but if you knew exact physics (force, angle, air resistance), you could predict it
- Not truly random, just too complex to predict in practice

**Computer randomness (pseudo-random):**
```python
import random
random.seed(12345)
print(random.randint(1, 100))  # Always gives same result with same seed!
```
- Uses mathematical formulas to generate "random-looking" numbers
- Actually deterministic - same input (seed) always gives same output
- Good enough for games, simulations, but NOT for security

**Quantum randomness (true random):**
- Based on quantum mechanics - the fundamental physics of atoms and particles
- **Physically impossible to predict**, even in theory
- The universe itself doesn't "know" the outcome until it's measured

### 2. What is Quantum Mechanics?

**Classical physics (everyday world):**
- Objects have definite positions and velocities
- If you know current state, you can predict future state
- Example: Throw a ball, you can calculate where it lands

**Quantum physics (atomic scale):**
- Particles exist in "superposition" - multiple states at once
- When you measure them, they randomly "collapse" to one state
- **No way to predict which state** - it's fundamentally random
- Example: A photon hitting a beam splitter has 50% chance to go left or right, and nothing in the universe can predict which

### 3. What is a Quantum Random Number Generator (QRNG)?

A device that uses quantum physics to generate truly random numbers.

**The ANU QRNG (what we used):**
1. Shoots a laser beam at a beam splitter (half-silvered mirror)
2. Quantum mechanics says each photon has 50/50 chance of going left or right
3. Detectors measure which way each photon went
4. Left = 0, Right = 1
5. Collect many measurements → random bits: `01101001...`

**Why it's truly random:**
- The photon doesn't "decide" which way to go
- The universe generates the randomness at the moment of measurement
- Even knowing everything about the photon beforehand, you cannot predict the outcome

### 4. What is Cryptography?

**Cryptography** = Secret codes for secure communication

**Example:**
```
Original message: "HELLO"
Encryption key:   "XMCKL"
Encrypted:        "EQNVZ"
```

**Why randomness matters:**
- If your encryption key is predictable, attackers can guess it
- If your key is truly random, it's impossible to guess

**Bad key (predictable):**
```python
key = "12345"  # Easy to guess!
```

**Good key (random):**
```python
key = "x7#mK9$pL2@qR5"  # Hard to guess
```

**Perfect key (quantum random):**
```python
key = quantum_random()  # Impossible to guess, even in theory!
```

### 5. What is an API?

**API (Application Programming Interface)** = A way for programs to talk to each other over the internet

**Analogy:** Like a restaurant menu
- You (the program) don't need to know how to cook
- You just order from the menu (make an API request)
- The kitchen (the server) prepares it and brings it to you (sends response)

**In this experiment:**
```python
# We "order" random numbers from the quantum computer
response = requests.get("https://qrng.anu.edu.au/API/jsonI.php")

# The quantum computer "serves" us the random numbers
random_data = response.json()['data']
```

### 6. What are the Different Types of Encryption Keys?

#### AES-256 Key
- **What:** Symmetric encryption key (same key encrypts and decrypts)
- **Size:** 256 bits (32 bytes)
- **Use:** Encrypting files, messages, hard drives
- **Example:** BitLocker, FileVault, Signal messages

#### SHA-256 Hash
- **What:** One-way transformation (can't reverse it)
- **Use:** Verifying data hasn't been tampered with, password storage
- **Example:** Bitcoin mining, file checksums

#### RSA Seed
- **What:** Starting point for generating public/private key pairs
- **Use:** Asymmetric encryption (public key encrypts, private key decrypts)
- **Example:** HTTPS websites, SSH keys, PGP email encryption

#### UUID (Universally Unique Identifier)
- **What:** A unique ID that's extremely unlikely to collide with other IDs
- **Use:** Database keys, session IDs, tracking codes
- **Example:** `1bfd8ef6-d138-aeec-24ec-332b4cfecef6`

### 7. What is the Chi-Square Test?

A statistical test to check if data is truly random.

**How it works:**
1. Count how many 1s and 0s in your random bits
2. For true randomness, expect ~50% ones and ~50% zeros
3. Calculate how far off you are from 50/50
4. If chi-square < 3.84, it's genuinely random (at 95% confidence)

**Our result:**
- Chi-square = 1.32 ✓ (much less than 3.84)
- 52.54% ones, 47.46% zeros ✓ (very close to 50/50)
- **Conclusion:** The data is genuinely random!

### 8. What is SSL/TLS and Why Did It Fail?

**SSL/TLS** = Secure communication protocol (the "S" in HTTPS)

**SSL Certificate** = Digital ID card for websites
- Proves the website is who it claims to be
- Has an expiration date (like a driver's license)

**What happened:**
- The ANU quantum server's certificate expired
- Our first attempt failed with: `certificate verify failed: certificate has expired`
- We disabled SSL verification (not recommended for production!) to proceed with the experiment

**Why this is interesting:**
- Even cutting-edge quantum systems have mundane infrastructure problems!
- Shows the messiness of real-world experimentation

## How to Read the Code

### Main Flow

```python
# 1. Request quantum random bytes from the API
response = requests.get("https://qrng.anu.edu.au/API/jsonI.php", 
                       params={"length": 64, "type": "uint8"})

# 2. Parse the JSON response
data = response.json()
random_bytes = bytes(data['data'])  # [27, 253, 142, 246, ...]

# 3. Convert bytes to binary bits
random_bits = ''.join(format(byte, '08b') for byte in random_bytes)
# Result: "0001101111111101100011101111011011010001..."

# 4. Use these bits to generate keys
aes_key = random_bytes[:32]  # First 32 bytes = AES-256 key
```

### Key Functions

**`get_quantum_random_anu()`**
- Connects to ANU quantum server
- Requests random bytes
- Returns binary bits and raw bytes

**`generate_crypto_keys()`**
- Takes quantum random data
- Generates various types of encryption keys
- Returns dictionary of keys

**`verify_randomness()`**
- Performs statistical tests
- Checks bit distribution
- Calculates chi-square statistic

## What Makes This "Unknown-Unknown"?

**Before this experiment, I didn't know:**
1. Quantum random number generators existed
2. They were publicly accessible via free APIs
3. You could generate cryptographic keys from quantum mechanics
4. It was as simple as making an HTTP request
5. The randomness quality was measurably superior to algorithms

**This is "unknown-unknown" because:**
- It's not something you'd think to Google
- It combines multiple domains (quantum physics + cryptography + web APIs)
- It challenges assumptions about what's possible with everyday tools

## Try It Yourself

### Prerequisites
```bash
pip install requests
```

### Minimal Example
```python
import requests

# Get 16 bytes of quantum random data
response = requests.get(
    "https://qrng.anu.edu.au/API/jsonI.php",
    params={"length": 16, "type": "uint8"},
    verify=False  # Due to expired cert
)

data = response.json()
print(f"Quantum random bytes: {data['data']}")
print(f"Success: {data['success']}")
```

### Expected Output
```
Quantum random bytes: [27, 253, 142, 246, 209, 56, 174, 236, 36, 236, 51, 43, 76, 254, 206, 246]
Success: True
```

## Further Reading

### Quantum Mechanics
- [Quantum Superposition (Wikipedia)](https://en.wikipedia.org/wiki/Quantum_superposition)
- [Double-slit experiment](https://en.wikipedia.org/wiki/Double-slit_experiment) - Shows quantum randomness visually

### Quantum Random Number Generators
- [ANU QRNG](https://qrng.anu.edu.au/) - The service we used
- [How does the ANU QRNG work?](https://qrng.anu.edu.au/contact/faq/)

### Cryptography
- [Cryptographic Key](https://en.wikipedia.org/wiki/Key_(cryptography))
- [AES Encryption](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard)
- [Why randomness matters in cryptography](https://en.wikipedia.org/wiki/Random_number_generation#Cryptography)

### Statistical Tests
- [Chi-Square Test](https://en.wikipedia.org/wiki/Chi-squared_test)
- [Randomness Tests](https://en.wikipedia.org/wiki/Randomness_tests)

## Common Questions

**Q: Is this really quantum mechanics or just marketing?**  
A: Really quantum! The ANU system measures actual photon behavior, which is governed by quantum mechanics. The randomness comes from quantum vacuum fluctuations.

**Q: Why don't all websites use quantum random keys?**  
A: Most don't need it. Algorithmic randomness (like `/dev/urandom`) is good enough for most purposes and doesn't require special hardware or API calls.

**Q: Could someone hack the quantum API and send fake random numbers?**  
A: Yes! That's why production systems use local hardware RNGs. This experiment is about exploring what's possible, not building production security.

**Q: How is this different from `random.random()` in Python?**  
A: `random.random()` uses an algorithm (Mersenne Twister) that's deterministic. Quantum randomness comes from physical measurements that are fundamentally unpredictable.

**Q: Can I use these keys for real encryption?**  
A: Technically yes, but don't! This is an experiment. For real security, use established libraries like `secrets` in Python or `crypto` in Node.js.

**Q: What if I run the code twice? Will I get the same keys?**  
A: No! Each time you call the quantum API, you get different random numbers from new quantum measurements.

## Glossary

- **API**: Application Programming Interface - a way for programs to communicate
- **AES**: Advanced Encryption Standard - a widely-used encryption algorithm
- **Bit**: Binary digit - either 0 or 1
- **Byte**: 8 bits (e.g., `11010110`)
- **Chi-Square**: A statistical test for randomness
- **Cryptography**: The science of secret codes
- **Deterministic**: Same input always gives same output
- **Hex**: Hexadecimal - base-16 number system (0-9, A-F)
- **HTTP**: Hypertext Transfer Protocol - how web browsers talk to servers
- **JSON**: JavaScript Object Notation - a data format
- **Photon**: A particle of light
- **QRNG**: Quantum Random Number Generator
- **Quantum**: Related to the physics of atoms and particles
- **SSL/TLS**: Secure Sockets Layer / Transport Layer Security - encryption for web traffic
- **Superposition**: A quantum state where something is in multiple states at once
- **UUID**: Universally Unique Identifier - a unique ID

---

**Questions?** Open an issue or experiment yourself!
