#!/usr/bin/env python3
"""Performance profiling script for syntax highlighter.

Measures highlighting performance with various instruction sets and cache behavior.
Run this to benchmark highlighting performance and identify bottlenecks.

Usage:
    python -m caspoon.scripts.profile_highlighter
    python caspoon/scripts/profile_highlighter.py
"""

import sys
import time
from statistics import mean, median, stdev
from typing import List

from caspoon.ui.syntax import AsmHighlighter
from caspoon.ui.syntax.arch_manager import get_instruction_classifier
from caspoon.ui.syntax.schemes import get_default_scheme


# Test data sets for various architectures
X86_INSTRUCTIONS = [
    # Data movement
    "mov rax, rbx",
    "mov qword [rsp+0x10], rax",
    "lea rdi, [rip+0x2004]",
    "push rbp",
    "pop rax",
    "xchg rax, rbx",
    
    # Arithmetic
    "add rax, 0x10",
    "sub rsp, 0x28",
    "imul rax, rcx, 4",
    "inc rdi",
    "dec rcx",
    
    # Logic
    "and rax, 0xff",
    "or rbx, rbx",
    "xor rax, rax",
    "test eax, eax",
    "not rdx",
    
    # Control flow
    "call 0x401000",
    "ret",
    "jmp 0x401050",
    "je 0x401020",
    "jne 0x401030",
    "jg 0x401040",
    "jl 0x401060",
    
    # Comparison
    "cmp rax, rbx",
    "cmp qword [rsp+0x8], 0",
    
    # Stack operations
    "push qword [rbp-0x8]",
    "pop r15",
    
    # Bit manipulation
    "shl rax, 4",
    "shr rbx, 2",
    "rol ecx, 8",
    "ror edx, 16",
    
    # String operations
    "movs byte [rdi], [rsi]",
    "rep movsb",
    "scas byte [rdi]",
    
    # System
    "syscall",
    "nop",
    "int 0x80",
]

ARM_INSTRUCTIONS = [
    # Data movement
    "mov r0, r1",
    "mov r0, #0x10",
    "movw r2, #0x1234",
    "movt r2, #0x5678",
    
    # Load/Store
    "ldr r0, [r1]",
    "ldr r0, [r1, #4]",
    "ldr r0, [r1, r2]",
    "str r2, [sp, #0x10]",
    "str r3, [r1], #4",
    "ldm r0, {r1, r2, r3}",
    "stm sp!, {r4, r5, r6, lr}",
    
    # ARM64 load/store
    "ldr x0, [x1, #8]",
    "str w2, [sp, #0x10]",
    "ldp x0, x1, [sp, #0x10]",
    "stp x2, x3, [sp, #-0x20]!",
    
    # Arithmetic
    "add r0, r1, r2",
    "add r0, r1, #0x10",
    "sub r0, r1, r2",
    "mul r0, r1, r2",
    
    # ARM64 arithmetic
    "add x0, x1, x2",
    "sub w0, w1, #0x10",
    
    # Logic
    "and r0, r1, r2",
    "orr r0, r1, r2",
    "eor r0, r1, r2",
    "bic r0, r1, r2",
    
    # Control flow
    "b 0x8000",
    "beq 0x8010",
    "bne 0x8020",
    "bl 0x8100",
    "blx r0",
    "bx lr",
    
    # ARM64 control flow
    "br x0",
    "blr x1",
    "ret",
    "b.eq 0x10000",
    "cbz x0, 0x10010",
    "cbnz w1, 0x10020",
    
    # Comparison
    "cmp r0, r1",
    "cmp r0, #0",
    "tst r0, r1",
]

MIPS_INSTRUCTIONS = [
    # Data movement
    "move $v0, $a0",
    "li $t0, 0x1000",
    "la $t1, label",
    
    # Load/Store
    "lw $t0, 0($sp)",
    "lw $t1, 4($sp)",
    "sw $t2, 8($sp)",
    "lb $t0, 0($a0)",
    "sb $t1, 1($a1)",
    "lh $t2, 2($a2)",
    "sh $t3, 3($a3)",
    
    # MIPS64
    "ld $t0, 0($sp)",
    "sd $t1, 8($sp)",
    
    # Arithmetic
    "add $t0, $t1, $t2",
    "addi $t0, $t1, 10",
    "sub $t0, $t1, $t2",
    "mul $t0, $t1, $t2",
    "div $t0, $t1",
    
    # Logic
    "and $t0, $t1, $t2",
    "or $t0, $t1, $t2",
    "xor $t0, $t1, $t2",
    "nor $t0, $t1, $t2",
    "andi $t0, $t1, 0xff",
    
    # Control flow
    "j 0x400000",
    "jr $ra",
    "jal 0x400100",
    "jalr $t0",
    "beq $t0, $t1, label",
    "bne $t0, $t1, label",
    "bgtz $t0, label",
    "blez $t0, label",
    
    # Comparison
    "slt $t0, $t1, $t2",
    "slti $t0, $t1, 10",
    
    # Shifts
    "sll $t0, $t1, 2",
    "srl $t0, $t1, 2",
    "sra $t0, $t1, 2",
    
    # System
    "syscall",
    "nop",
]


def profile_highlighting(
    instructions: List[str],
    arch: str = "x86_64",
    iterations: int = 100,
    warmup: int = 10
) -> dict:
    """Profile highlighting performance.
    
    Args:
        instructions: List of instruction strings to test
        arch: Architecture name ('x86_64', 'arm', 'mips')
        iterations: Number of iterations for timing
        warmup: Number of warmup iterations before timing
        
    Returns:
        Dictionary with timing statistics and cache info
    """
    # Setup
    classifier = get_instruction_classifier(arch)
    highlighter = AsmHighlighter(
        color_scheme=get_default_scheme(),
        instruction_classifier=classifier,
        cache_size=1000
    )
    
    # Measure without cache (cold cache - always new instructions)
    times_cold = []
    highlighter.clear_cache()
    highlighter.disable_cache()
    
    # Warmup JIT/interpreter
    for _ in range(warmup):
        for instr in instructions:
            highlighter.highlight_instruction(instr, "0x401000")
    
    # Actual timing - each iteration with fresh instructions to avoid any caching
    for iteration in range(iterations):
        start = time.perf_counter()
        # Use different addresses to ensure no accidental caching
        for idx, instr in enumerate(instructions):
            addr = f"0x{0x401000 + iteration * 1000 + idx:x}"
            highlighter.highlight_instruction(instr, addr)
        elapsed = time.perf_counter() - start
        times_cold.append(elapsed)
    
    # Measure with cache (warm cache - repeated instructions)
    times_warm = []
    highlighter.clear_cache()
    highlighter.enable_cache()
    
    # Warmup cache
    for _ in range(warmup):
        for instr in instructions:
            highlighter.highlight_instruction(instr, "0x401000")
    
    # Pre-populate cache with common patterns
    for instr in instructions:
        highlighter.highlight_instruction(instr, "0x401000")
    
    # Actual timing with warm cache - repeatedly highlight same instructions
    for _ in range(iterations):
        start = time.perf_counter()
        for instr in instructions:
            # Use same address to get cache hits
            highlighter.highlight_instruction(instr, "0x401000")
        elapsed = time.perf_counter() - start
        times_warm.append(elapsed)
    
    # Calculate statistics
    cold_mean = mean(times_cold)
    warm_mean = mean(times_warm)
    speedup = cold_mean / warm_mean if warm_mean > 0 else 0
    
    return {
        "arch": arch,
        "num_instructions": len(instructions),
        "iterations": iterations,
        "cold": {
            "mean": cold_mean,
            "median": median(times_cold),
            "stdev": stdev(times_cold) if len(times_cold) > 1 else 0,
            "min": min(times_cold),
            "max": max(times_cold),
        },
        "warm": {
            "mean": warm_mean,
            "median": median(times_warm),
            "stdev": stdev(times_warm) if len(times_warm) > 1 else 0,
            "min": min(times_warm),
            "max": max(times_warm),
        },
        "speedup": speedup,
        "cache_info": highlighter.get_cache_info(),
    }


def format_time_ms(seconds: float) -> str:
    """Format time in milliseconds with appropriate precision."""
    ms = seconds * 1000
    if ms < 1:
        return f"{ms*1000:.2f}µs"
    else:
        return f"{ms:.3f}ms"


def format_throughput(num_instructions: int, time_seconds: float) -> str:
    """Format throughput in instructions per second."""
    if time_seconds > 0:
        throughput = num_instructions / time_seconds
        if throughput >= 1_000_000:
            return f"{throughput/1_000_000:.2f}M instr/s"
        elif throughput >= 1000:
            return f"{throughput/1000:.2f}K instr/s"
        else:
            return f"{throughput:.1f} instr/s"
    return "N/A"


def print_results(results: dict) -> None:
    """Print profiling results in a readable format."""
    print(f"\n{'=' * 70}")
    print(f"Architecture: {results['arch'].upper()}")
    print(f"Instructions: {results['num_instructions']}")
    print(f"Iterations: {results['iterations']}")
    print(f"{'=' * 70}")
    
    # Cold cache results
    cold = results["cold"]
    print(f"\n  COLD CACHE (no caching):")
    print(f"    Mean:       {format_time_ms(cold['mean'])}")
    print(f"    Median:     {format_time_ms(cold['median'])}")
    print(f"    Std Dev:    {format_time_ms(cold['stdev'])}")
    print(f"    Range:      {format_time_ms(cold['min'])} - {format_time_ms(cold['max'])}")
    print(f"    Throughput: {format_throughput(results['num_instructions'], cold['mean'])}")
    
    # Warm cache results
    warm = results["warm"]
    print(f"\n  WARM CACHE (with LRU caching):")
    print(f"    Mean:       {format_time_ms(warm['mean'])}")
    print(f"    Median:     {format_time_ms(warm['median'])}")
    print(f"    Std Dev:    {format_time_ms(warm['stdev'])}")
    print(f"    Range:      {format_time_ms(warm['min'])} - {format_time_ms(warm['max'])}")
    print(f"    Throughput: {format_throughput(results['num_instructions'], warm['mean'])}")
    
    # Speedup
    print(f"\n  PERFORMANCE IMPROVEMENT:")
    print(f"    Speedup:    {results['speedup']:.2f}x faster")
    print(f"    Reduction:  {(1 - 1/results['speedup'])*100:.1f}% time saved")
    
    # Cache statistics
    cache = results["cache_info"]
    if cache:
        hit_rate = cache['hits'] / (cache['hits'] + cache['misses']) * 100 if (cache['hits'] + cache['misses']) > 0 else 0
        print(f"\n  CACHE STATISTICS:")
        print(f"    Hits:       {cache['hits']}")
        print(f"    Misses:     {cache['misses']}")
        print(f"    Hit Rate:   {hit_rate:.1f}%")
        print(f"    Size:       {cache['size']} / {cache['maxsize']}")


def print_summary_table(all_results: List[dict]) -> None:
    """Print a summary table comparing all architectures."""
    print(f"\n{'=' * 70}")
    print("SUMMARY COMPARISON")
    print(f"{'=' * 70}")
    print(f"\n{'Architecture':<15} {'Cold (ms)':<12} {'Warm (ms)':<12} {'Speedup':<10} {'Throughput':<15}")
    print(f"{'-'*70}")
    
    for result in all_results:
        arch = result['arch'].upper()
        cold_ms = result['cold']['mean'] * 1000
        warm_ms = result['warm']['mean'] * 1000
        speedup = result['speedup']
        throughput = format_throughput(result['num_instructions'], result['warm']['mean'])
        
        print(f"{arch:<15} {cold_ms:>9.3f}    {warm_ms:>9.3f}    {speedup:>6.2f}x    {throughput:<15}")


def main():
    """Run profiling tests and display results."""
    print("=" * 70)
    print("SYNTAX HIGHLIGHTER PERFORMANCE PROFILING")
    print("=" * 70)
    print("\nThis script measures highlighting performance across different")
    print("architectures and cache configurations.")
    
    # Important note about the cache
    print("\n" + "!" * 70)
    print("NOTE: Cache Implementation Observation")
    print("!" * 70)
    print("\nThe current cache implementation stores markup strings and converts")
    print("them back to Text objects. This conversion overhead may negate some")
    print("of the parsing/highlighting performance gains.")
    print("\nThe cache is most beneficial when:")
    print("  - Displaying large disassemblies with repeated instruction patterns")
    print("  - The same instructions appear many times (common in loops)")
    print("  - Memory constraints allow for large cache sizes")
    print("\nFor typical usage (viewing disassembly once), the cache overhead")
    print("may exceed the benefits. Cache is most valuable for interactive")
    print("exploration of the same binary where instructions are re-rendered.")
    
    print(f"\nRunning benchmarks...")
    
    all_results = []
    
    # Profile x86_64
    print("\n[1/3] Profiling x86_64 instructions...")
    results_x86 = profile_highlighting(X86_INSTRUCTIONS, "x86_64", iterations=100)
    print_results(results_x86)
    all_results.append(results_x86)
    
    # Profile ARM
    print("\n[2/3] Profiling ARM instructions...")
    results_arm = profile_highlighting(ARM_INSTRUCTIONS, "arm", iterations=100)
    print_results(results_arm)
    all_results.append(results_arm)
    
    # Profile MIPS
    print("\n[3/3] Profiling MIPS instructions...")
    results_mips = profile_highlighting(MIPS_INSTRUCTIONS, "mips", iterations=100)
    print_results(results_mips)
    all_results.append(results_mips)
    
    # Print summary
    print_summary_table(all_results)
    
    # Final analysis
    avg_speedup = mean([r['speedup'] for r in all_results])
    print(f"\n{'=' * 70}")
    print("ANALYSIS")
    print(f"{'=' * 70}")
    print(f"\nAverage speedup across all architectures: {avg_speedup:.2f}x")
    print(f"Cache hit rate: {mean([r['cache_info']['hits']/(r['cache_info']['hits']+r['cache_info']['misses'])*100 for r in all_results]):.1f}%")
    
    if avg_speedup >= 5:
        print("\n✓ GOOD: Caching provides significant speedup (>=5x)")
        print("  Cache is beneficial for this workload.")
    elif avg_speedup >= 2:
        print("\n⚠ MODERATE: Caching provides moderate speedup (2-5x)")
        print("  Cache may help in some scenarios.")
    elif avg_speedup >= 1:
        print("\n⚠ MARGINAL: Caching provides minimal benefit (1-2x)")
        print("  Cache overhead is close to the benefit.")
    else:
        print("\n⚠ OVERHEAD: Cache adds overhead (speedup <1x)")
        print("  The Text.from_markup() conversion cost exceeds the benefit.")
        print("  Consider caching the parsed result instead of markup strings,")
        print("  or only using cache for truly repeated patterns.")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    
    if avg_speedup < 2:
        print("\nBased on these results, consider:")
        print("  1. Cache the parsed operands/patterns, not the Text markup")
        print("  2. Only enable cache for interactive/GUI modes")
        print("  3. Measure real-world usage patterns (loops, repeated code)")
        print("  4. Consider alternative caching strategies:")
        print("     - Cache parsed operands separately")
        print("     - Cache instruction classifications only")
        print("     - Use cache only when hit rate exceeds threshold")
    else:
        print("\nCache is working well! Benefits:")
        print("  - Faster rendering of repeated instruction patterns")
        print("  - Good for interactive disassembly viewing")
        print("  - Scales well with larger code bases")
    
    print(f"\n{'=' * 70}")
    print("PROFILING COMPLETE")
    print(f"{'=' * 70}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
