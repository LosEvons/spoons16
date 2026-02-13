# Test Binary Fixtures

## Overview
This directory contains test binaries used for caspoon testing.

## Test Binaries

### test_hello_x64
- **Architecture**: x86-64
- **Purpose**: Basic functionality testing
- **Features**: Standard ELF, not stripped, PIE disabled

### test_hello_x86
- **Architecture**: x86 (32-bit)
- **Purpose**: 32-bit support testing
- **Features**: 32-bit ELF (if gcc -m32 available)

### test_stripped
- **Architecture**: x86-64
- **Purpose**: Test stripped binary detection
- **Features**: Debug symbols stripped

### test_with_pie
- **Architecture**: x86-64
- **Purpose**: Test security feature detection
- **Features**: PIE, stack canary, NX, full RELRO

## Building Test Binaries

```bash
cd src/
make
```

## Cleanup

```bash
cd src/
make clean
```
