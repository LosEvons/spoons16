"""Comprehensive instruction database for x86/x64 assembly.

This module provides detailed instruction classifications for x86/x64
assembly code, organized by instruction type for syntax highlighting
and analysis purposes.
"""

from .schemes import InstructionType

# Comprehensive x86/x64 instruction database
# Maps instruction types to sets of instruction mnemonics

X86_64_INSTRUCTIONS = {
    InstructionType.JUMP: {
        # Unconditional jumps
        'jmp', 'jmpq', 'jmpl', 'jmpw',
        # Conditional jumps
        'je', 'jz',  # equal/zero
        'jne', 'jnz',  # not equal/not zero
        'jg', 'jnle',  # greater/not less or equal (signed)
        'jge', 'jnl',  # greater or equal/not less (signed)
        'jl', 'jnge',  # less/not greater or equal (signed)
        'jle', 'jng',  # less or equal/not greater (signed)
        'ja', 'jnbe',  # above/not below or equal (unsigned)
        'jae', 'jnb', 'jnc',  # above or equal/not below/not carry (unsigned)
        'jb', 'jnae', 'jc',  # below/not above or equal/carry (unsigned)
        'jbe', 'jna',  # below or equal/not above (unsigned)
        'jo',  # overflow
        'jno',  # not overflow
        'js',  # sign
        'jns',  # not sign
        'jp', 'jpe',  # parity/parity even
        'jnp', 'jpo',  # not parity/parity odd
        # Special conditional jumps
        'jcxz', 'jecxz', 'jrcxz',  # jump if CX/ECX/RCX is zero
        # Loop instructions
        'loop', 'loope', 'loopz', 'loopne', 'loopnz',
    },
    
    InstructionType.CALL: {
        'call', 'callq', 'calll', 'callw',
    },
    
    InstructionType.RETURN: {
        'ret', 'retq', 'retl', 'retw', 'retn',
        'retf', 'retfq', 'retfl', 'retfw',
        'iret', 'iretd', 'iretq',
    },
    
    InstructionType.MOVE: {
        # Basic move
        'mov', 'movq', 'movl', 'movw', 'movb',
        # Move with zero/sign extension
        'movzx', 'movzb', 'movzw', 'movzl', 'movzq',
        'movsx', 'movsb', 'movsw', 'movsl', 'movsq',
        'movsxd', 'movsbq', 'movswq', 'movslq',
        # Load effective address
        'lea', 'leaq', 'leal', 'leaw',
        # Exchange
        'xchg', 'xchgq', 'xchgl', 'xchgw', 'xchgb',
        # Conditional move
        'cmove', 'cmovz', 'cmovne', 'cmovnz',
        'cmovg', 'cmovge', 'cmovl', 'cmovle',
        'cmova', 'cmovae', 'cmovb', 'cmovbe',
        'cmovo', 'cmovno', 'cmovs', 'cmovns',
        'cmovp', 'cmovnp',
        # Set byte on condition
        'sete', 'setz', 'setne', 'setnz',
        'setg', 'setge', 'setl', 'setle',
        'seta', 'setae', 'setb', 'setbe',
        'seto', 'setno', 'sets', 'setns',
        'setp', 'setnp',
    },
    
    InstructionType.ARITHMETIC: {
        # Addition
        'add', 'addq', 'addl', 'addw', 'addb',
        'adc', 'adcq', 'adcl', 'adcw', 'adcb',  # add with carry
        # Subtraction
        'sub', 'subq', 'subl', 'subw', 'subb',
        'sbb', 'sbbq', 'sbbl', 'sbbw', 'sbbb',  # subtract with borrow
        # Multiplication
        'mul', 'mulq', 'mull', 'mulw', 'mulb',
        'imul', 'imulq', 'imull', 'imulw', 'imulb',
        # Division
        'div', 'divq', 'divl', 'divw', 'divb',
        'idiv', 'idivq', 'idivl', 'idivw', 'idivb',
        # Increment/Decrement
        'inc', 'incq', 'incl', 'incw', 'incb',
        'dec', 'decq', 'decl', 'decw', 'decb',
        # Negate
        'neg', 'negq', 'negl', 'negw', 'negb',
        # Misc arithmetic
        'aaa', 'aad', 'aam', 'aas',  # ASCII adjust
        'daa', 'das',  # Decimal adjust
        'cbw', 'cwde', 'cdqe',  # Convert byte/word/dword
        'cwd', 'cdq', 'cqo',  # Convert word/dword/qword to double
    },
    
    InstructionType.LOGIC: {
        # Logical operations
        'and', 'andq', 'andl', 'andw', 'andb',
        'or', 'orq', 'orl', 'orw', 'orb',
        'xor', 'xorq', 'xorl', 'xorw', 'xorb',
        'not', 'notq', 'notl', 'notw', 'notb',
        # Shift instructions
        'shl', 'shlq', 'shll', 'shlw', 'shlb',
        'sal', 'salq', 'sall', 'salw', 'salb',
        'shr', 'shrq', 'shrl', 'shrw', 'shrb',
        'sar', 'sarq', 'sarl', 'sarw', 'sarb',
        # Rotate instructions
        'rol', 'rolq', 'roll', 'rolw', 'rolb',
        'ror', 'rorq', 'rorl', 'rorw', 'rorb',
        'rcl', 'rclq', 'rcll', 'rclw', 'rclb',
        'rcr', 'rcrq', 'rcrl', 'rcrw', 'rcrb',
        # Bit manipulation
        'bt', 'btq', 'btl', 'btw',  # bit test
        'bts', 'btsq', 'btsl', 'btsw',  # bit test and set
        'btr', 'btrq', 'btrl', 'btrw',  # bit test and reset
        'btc', 'btcq', 'btcl', 'btcw',  # bit test and complement
        'bsf', 'bsfq', 'bsfl', 'bsfw',  # bit scan forward
        'bsr', 'bsrq', 'bsrl', 'bsrw',  # bit scan reverse
        'bswap', 'bswapq', 'bswapl',  # byte swap
    },
    
    InstructionType.STACK: {
        # Push/Pop
        'push', 'pushq', 'pushl', 'pushw', 'pushb',
        'pop', 'popq', 'popl', 'popw', 'popb',
        'pusha', 'pushad', 'popa', 'popad',
        'pushf', 'pushfq', 'pushfd', 'pushfw',
        'popf', 'popfq', 'popfd', 'popfw',
        # Stack frame operations
        'enter', 'enterq', 'enterl',
        'leave', 'leaveq', 'leavel',
    },
    
    InstructionType.COMPARE: {
        'cmp', 'cmpq', 'cmpl', 'cmpw', 'cmpb',
        'test', 'testq', 'testl', 'testw', 'testb',
    },
    
    # New instruction types for extended classification
    InstructionType.OTHER: {
        # NOP and variants
        'nop', 'nopq', 'nopl', 'nopw',
        # Undefined/trap
        'ud2', 'ud2a', 'ud2b',
        # Hints
        'hint_nop',
        # Processor identification
        'cpuid',
        # Time stamp counter
        'rdtsc', 'rdtscp',
        # Performance monitoring
        'rdpmc',
        # Model specific registers
        'rdmsr', 'wrmsr',
        # Flags
        'clc', 'stc', 'cmc',  # carry flag
        'cld', 'std',  # direction flag
        'cli', 'sti',  # interrupt flag
        'clac', 'stac',  # alignment check flag
        # Segment operations
        'lds', 'les', 'lfs', 'lgs', 'lss',
        # Table operations
        'lgdt', 'sgdt', 'lidt', 'sidt',
        'lldt', 'sldt', 'ltr', 'str',
        # Memory operations
        'xlat', 'xlatb',
        # Bound check
        'bound',
        # Convert
        'bswap',
    },
}

# String operations (often used with REP prefixes)
STRING_INSTRUCTIONS = {
    'cmps', 'cmpsb', 'cmpsw', 'cmpsd', 'cmpsq',  # compare strings
    'lods', 'lodsb', 'lodsw', 'lodsd', 'lodsq',  # load string
    'stos', 'stosb', 'stosw', 'stosd', 'stosq',  # store string
    'scas', 'scasb', 'scasw', 'scasd', 'scasq',  # scan string
    'movs', 'movsb', 'movsw', 'movsd', 'movsq',  # move string
    'ins', 'insb', 'insw', 'insd',  # input string
    'outs', 'outsb', 'outsw', 'outsd',  # output string
    # Prefixes
    'rep', 'repe', 'repz', 'repne', 'repnz',
}

# System and privileged instructions
SYSTEM_INSTRUCTIONS = {
    # Interrupts
    'int', 'int3', 'into',
    'iret', 'iretd', 'iretq',
    # System calls
    'syscall', 'sysret',
    'sysenter', 'sysexit',
    # I/O operations
    'in', 'inb', 'inw', 'ind',
    'out', 'outb', 'outw', 'outd',
    # Halt
    'hlt',
    # Cache control
    'invd', 'wbinvd',
    'invlpg', 'invpcid',
    'clflush', 'clflushopt',
    # TLB control
    'invlpg',
    # Memory fence
    'lfence', 'sfence', 'mfence',
    # Lock prefix
    'lock',
    # Monitor/wait
    'monitor', 'mwait',
    # Protection
    'verr', 'verw',
    'lar', 'lsl',
    'arpl',
    # Task switch
    'ltr', 'str',
    # CR register access
    'mov',  # when used with CR registers
    # Debug registers
    'mov',  # when used with DR registers
}

# FPU instructions
FPU_INSTRUCTIONS = {
    # Load/Store
    'fld', 'fst', 'fstp',
    'fild', 'fist', 'fistp',
    'fbld', 'fbstp',
    # Arithmetic
    'fadd', 'faddp', 'fiadd',
    'fsub', 'fsubp', 'fisub', 'fsubr', 'fsubrp', 'fisubr',
    'fmul', 'fmulp', 'fimul',
    'fdiv', 'fdivp', 'fidiv', 'fdivr', 'fdivrp', 'fidivr',
    'fsqrt', 'fabs', 'fchs',
    # Compare
    'fcom', 'fcomp', 'fcompp', 'ficom', 'ficomp',
    'fcomi', 'fcomip', 'fucomi', 'fucomip',
    'ftst', 'fxam',
    # Transcendental
    'fsin', 'fcos', 'fsincos', 'fptan', 'fpatan',
    'f2xm1', 'fyl2x', 'fyl2xp1',
    # Control
    'finit', 'fninit', 'fclex', 'fnclex',
    'fldcw', 'fnstcw', 'fstcw',
    'fldenv', 'fnstenv', 'fstenv',
    'fsave', 'fnsave', 'frstor',
    # Stack operations
    'fxch', 'ffree', 'ffreep',
    # Constants
    'fld1', 'fldz', 'fldpi', 'fldl2e', 'fldl2t', 'fldlg2', 'fldln2',
    # Misc
    'fnop', 'fwait', 'wait',
}

# MMX instructions
MMX_INSTRUCTIONS = {
    # Data transfer
    'movd', 'movq',
    # Arithmetic
    'paddb', 'paddw', 'paddd', 'paddq',
    'paddsb', 'paddsw', 'paddusb', 'paddusw',
    'psubb', 'psubw', 'psubd', 'psubq',
    'psubsb', 'psubsw', 'psubusb', 'psubusw',
    'pmullw', 'pmulhw', 'pmulhuw',
    'pmaddwd',
    # Comparison
    'pcmpeqb', 'pcmpeqw', 'pcmpeqd',
    'pcmpgtb', 'pcmpgtw', 'pcmpgtd',
    # Logical
    'pand', 'pandn', 'por', 'pxor',
    # Shift
    'psllw', 'pslld', 'psllq',
    'psrlw', 'psrld', 'psrlq',
    'psraw', 'psrad',
    # Pack/Unpack
    'packsswb', 'packssdw', 'packuswb',
    'punpckhbw', 'punpckhwd', 'punpckhdq',
    'punpcklbw', 'punpcklwd', 'punpckldq',
    # Misc
    'emms',
}

# SSE instructions (partial list - basic coverage)
SSE_INSTRUCTIONS = {
    # Data movement
    'movaps', 'movups', 'movss', 'movsd',
    'movhps', 'movlps', 'movhlps', 'movlhps',
    'movmskps', 'movmskpd',
    'movdqa', 'movdqu',
    # Arithmetic
    'addps', 'addss', 'addpd', 'addsd',
    'subps', 'subss', 'subpd', 'subsd',
    'mulps', 'mulss', 'mulpd', 'mulsd',
    'divps', 'divss', 'divpd', 'divsd',
    'sqrtps', 'sqrtss', 'sqrtpd', 'sqrtsd',
    'rsqrtps', 'rsqrtss',
    'rcpps', 'rcpss',
    'minps', 'minss', 'minpd', 'minsd',
    'maxps', 'maxss', 'maxpd', 'maxsd',
    # Logical
    'andps', 'andpd', 'andnps', 'andnpd',
    'orps', 'orpd', 'xorps', 'xorpd',
    # Compare
    'cmpps', 'cmpss', 'cmppd', 'cmpsd',
    'comiss', 'comisd', 'ucomiss', 'ucomisd',
    # Conversion
    'cvtps2pd', 'cvtpd2ps', 'cvtss2sd', 'cvtsd2ss',
    'cvtpi2ps', 'cvtps2pi', 'cvttps2pi',
    'cvtpi2pd', 'cvtpd2pi', 'cvttpd2pi',
    'cvtsi2ss', 'cvtss2si', 'cvttss2si',
    'cvtsi2sd', 'cvtsd2si', 'cvttsd2si',
    'cvtdq2ps', 'cvtps2dq', 'cvttps2dq',
    'cvtdq2pd', 'cvtpd2dq', 'cvttpd2dq',
    # Pack/Unpack
    'unpckhps', 'unpcklps', 'unpckhpd', 'unpcklpd',
    'shufps', 'shufpd',
    # Cache control
    'prefetcht0', 'prefetcht1', 'prefetcht2', 'prefetchnta',
    'sfence',
}

# AVX instructions (partial list - basic coverage)
AVX_INSTRUCTIONS = {
    # Data movement
    'vmovaps', 'vmovups', 'vmovss', 'vmovsd',
    'vmovdqa', 'vmovdqu',
    'vmovapd', 'vmovupd',
    # Arithmetic
    'vaddps', 'vaddss', 'vaddpd', 'vaddsd',
    'vsubps', 'vsubss', 'vsubpd', 'vsubsd',
    'vmulps', 'vmulss', 'vmulpd', 'vmulsd',
    'vdivps', 'vdivss', 'vdivpd', 'vdivsd',
    'vsqrtps', 'vsqrtss', 'vsqrtpd', 'vsqrtsd',
    # Logical
    'vandps', 'vandpd', 'vandnps', 'vandnpd',
    'vorps', 'vorpd', 'vxorps', 'vxorpd',
    # Compare
    'vcmpps', 'vcmpss', 'vcmppd', 'vcmpsd',
    # Blend
    'vblendps', 'vblendpd', 'vblendvps', 'vblendvpd',
    # Broadcast
    'vbroadcastss', 'vbroadcastsd',
    # Insert/Extract
    'vinsertf128', 'vextractf128',
    'vinsertps', 'vextractps',
    # Permute
    'vperm2f128', 'vpermilps', 'vpermilpd',
    # Zero upper
    'vzeroupper', 'vzeroall',
}

# Combined SIMD instruction set
SIMD_INSTRUCTIONS = MMX_INSTRUCTIONS | SSE_INSTRUCTIONS | AVX_INSTRUCTIONS


def get_instruction_type(mnemonic: str) -> InstructionType:
    """Get the instruction type for a given mnemonic.
    
    Args:
        mnemonic: The instruction mnemonic (lowercase).
    
    Returns:
        The InstructionType for this mnemonic.
    """
    mnemonic = mnemonic.lower().strip()
    
    # Check main instruction categories
    for instr_type, instructions in X86_64_INSTRUCTIONS.items():
        if mnemonic in instructions:
            return instr_type
    
    # Check string operations (classify as MOVE for now)
    if mnemonic in STRING_INSTRUCTIONS:
        return InstructionType.MOVE
    
    # Check system instructions (classify as OTHER)
    if mnemonic in SYSTEM_INSTRUCTIONS:
        return InstructionType.OTHER
    
    # Check SIMD instructions (classify as OTHER)
    if mnemonic in SIMD_INSTRUCTIONS:
        return InstructionType.OTHER
    
    # Check FPU instructions (classify as ARITHMETIC)
    if mnemonic in FPU_INSTRUCTIONS:
        return InstructionType.ARITHMETIC
    
    return InstructionType.OTHER


def is_string_instruction(mnemonic: str) -> bool:
    """Check if a mnemonic is a string operation instruction.
    
    Args:
        mnemonic: The instruction mnemonic (lowercase).
    
    Returns:
        True if this is a string operation instruction.
    """
    return mnemonic.lower().strip() in STRING_INSTRUCTIONS


def is_system_instruction(mnemonic: str) -> bool:
    """Check if a mnemonic is a system/privileged instruction.
    
    Args:
        mnemonic: The instruction mnemonic (lowercase).
    
    Returns:
        True if this is a system/privileged instruction.
    """
    return mnemonic.lower().strip() in SYSTEM_INSTRUCTIONS


def is_simd_instruction(mnemonic: str) -> bool:
    """Check if a mnemonic is a SIMD instruction.
    
    Args:
        mnemonic: The instruction mnemonic (lowercase).
    
    Returns:
        True if this is a SIMD instruction (MMX/SSE/AVX).
    """
    return mnemonic.lower().strip() in SIMD_INSTRUCTIONS


def is_fpu_instruction(mnemonic: str) -> bool:
    """Check if a mnemonic is an FPU instruction.
    
    Args:
        mnemonic: The instruction mnemonic (lowercase).
    
    Returns:
        True if this is an FPU instruction.
    """
    return mnemonic.lower().strip() in FPU_INSTRUCTIONS
