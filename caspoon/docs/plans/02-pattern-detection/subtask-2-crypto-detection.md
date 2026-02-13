# Subtask 2: Cryptographic Detection

## Objective
Detect cryptographic constants, algorithms, and libraries in binaries.

## Implementation

### Known Constants Database (4 hours)
**Location**: `caspoon/patterns/crypto.py`

```python
CRYPTO_CONSTANTS = {
    'AES_SBOX': bytes([
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,
        0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        # ... full S-box
    ]),
    'SHA256_K': [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
        # ... 64 constants
    ],
    'MD5_INIT': [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476],
}
```

### Crypto Pattern Detectors (6 hours)
- AES S-box detector
- SHA constant detector
- RSA modulus detector (large prime numbers)
- Base64 table detector
- RC4 key scheduling detector

### Algorithm Recognition (4 hours)
Identify crypto operations by instruction patterns:
```python
def detect_aes_rounds(disasm: List[str]) -> bool:
    """Detect AES round operations."""
    # Look for AES-NI instructions or table lookups
    aes_instructions = ['aesenc', 'aesenclast', 'aesdec', 'aesdeclast']
    # Check for patterns
```

## Estimated Time: 14 hours

## Success Criteria
- [ ] Detects AES S-boxes with 95%+ accuracy
- [ ] Identifies SHA-256/SHA-1 constants
- [ ] Recognizes common crypto libraries (OpenSSL, etc.)
- [ ] Flags potential custom crypto implementations
