"""Comprehensive instruction database for MIPS assembly.

This module provides detailed instruction classifications for MIPS
assembly code, organized by instruction type for syntax highlighting
and analysis purposes.
"""

from .schemes import InstructionType

# Comprehensive MIPS instruction database
# Maps instruction types to sets of instruction mnemonics

MIPS_INSTRUCTIONS = {
    InstructionType.JUMP: {
        # Unconditional jumps
        'j', 'jr',  # jump, jump register
        # Conditional branches
        'beq', 'bne',  # branch if equal/not equal
        'bgtz', 'blez',  # branch if greater than/less than or equal to zero
        'bltz', 'bgez',  # branch if less than/greater than or equal to zero
        'bltzal', 'bgezal',  # branch and link (less than/greater than or equal to zero)
        # Branch likely (deprecated but still used)
        'beql', 'bnel', 'bgtzl', 'blezl', 'bltzl', 'bgezl',
        # MIPS32/64 additional branches
        'bc1f', 'bc1t',  # branch on FP false/true
        'bc1fl', 'bc1tl',  # branch on FP false/true likely
        # MIPS R6 compact branches
        'beqc', 'bnec', 'bltc', 'bgec', 'bltuc', 'bgeuc',
        'beqzc', 'bnezc', 'bltzc', 'bgezc', 'blezc', 'bgtzc',
        # Unconditional relative branches
        'b', 'bal',  # pseudo-instructions (b = beq $zero,$zero; bal = bgezal $zero)
    },

    InstructionType.CALL: {
        # Jump and link (function calls)
        'jal', 'jalr',  # jump and link, jump and link register
        'jalx',  # jump and link exchange (MIPS16)
        # MIPS R6
        'jialc', 'jic',  # jump indexed and link/compact
        'balc',  # branch and link compact
    },

    InstructionType.RETURN: set(),  # No explicit return instruction in MIPS

    InstructionType.MOVE: {
        # Load operations (data movement from memory)
        'lw', 'lh', 'lb', 'lhu', 'lbu',  # load word/halfword/byte (signed/unsigned)
        'lwl', 'lwr',  # load word left/right (unaligned)
        'lhl', 'lhr',  # load halfword left/right
        'll',  # load linked
        'ld', 'ldl', 'ldr',  # load doubleword (MIPS64)
        'lld',  # load linked doubleword
        # Store operations (data movement to memory)
        'sw', 'sh', 'sb',  # store word/halfword/byte
        'swl', 'swr',  # store word left/right (unaligned)
        'shl', 'shr',  # store halfword left/right
        'sc',  # store conditional
        'sd', 'sdl', 'sdr',  # store doubleword (MIPS64)
        'scd',  # store conditional doubleword
        # Move operations
        'move',  # pseudo-instruction (addu rd, rs, $zero)
        'mfhi', 'mflo',  # move from HI/LO
        'mthi', 'mtlo',  # move to HI/LO
        'mfcz', 'mtcz',  # move from/to coprocessor z
        'mfc0', 'mtc0',  # move from/to coprocessor 0 (system)
        'mfc1', 'mtc1',  # move from/to coprocessor 1 (FPU)
        'mfc2', 'mtc2',  # move from/to coprocessor 2
        # Load immediate and address
        'li', 'la',  # load immediate/address (pseudo-instructions)
        'lui',  # load upper immediate
        # Conditional move
        'movn', 'movz',  # move conditional on not zero/zero
        'movf', 'movt',  # move conditional on FP false/true
    },

    InstructionType.ARITHMETIC: {
        # Addition
        'add', 'addu',  # add (with/without overflow trap)
        'addi', 'addiu',  # add immediate (with/without overflow trap)
        'dadd', 'daddu', 'daddi', 'daddiu',  # doubleword add (MIPS64)
        # Subtraction
        'sub', 'subu',  # subtract (with/without overflow trap)
        'dsub', 'dsubu',  # doubleword subtract (MIPS64)
        # Multiplication
        'mult', 'multu',  # multiply (signed/unsigned)
        'mul', 'muh', 'mulu', 'muhu',  # multiply (MIPS32 Release 6)
        'dmult', 'dmultu',  # doubleword multiply (MIPS64)
        'dmul', 'dmuh', 'dmulu', 'dmuhu',  # doubleword multiply (MIPS64 R6)
        'madd', 'maddu',  # multiply and add to HI/LO
        'msub', 'msubu',  # multiply and subtract from HI/LO
        # Division
        'div', 'divu',  # divide (signed/unsigned)
        'ddiv', 'ddivu',  # doubleword divide (MIPS64)
        'mod', 'modu',  # modulo (MIPS32 R6)
        'dmod', 'dmodu',  # doubleword modulo (MIPS64 R6)
        # Negate
        'neg', 'negu',  # negate (pseudo-instruction)
        # Absolute value
        'abs',  # absolute value (pseudo-instruction)
    },

    InstructionType.LOGIC: {
        # Logical operations
        'and', 'or', 'xor', 'nor',  # bitwise and/or/xor/nor
        'andi', 'ori', 'xori',  # bitwise immediate
        'not',  # bitwise not (pseudo-instruction: nor rd, rs, $zero)
        # Shift operations
        'sll', 'srl', 'sra',  # shift left logical, right logical, right arithmetic
        'sllv', 'srlv', 'srav',  # shift variable
        'dsll', 'dsrl', 'dsra',  # doubleword shifts (MIPS64)
        'dsllv', 'dsrlv', 'dsrav',  # doubleword shifts variable
        'dsll32', 'dsrl32', 'dsra32',  # doubleword shifts by 32+
        # Rotate (MIPS32 Release 2)
        'rotr', 'rotrv',  # rotate right
        'drotr', 'drotrv', 'drotr32',  # doubleword rotate (MIPS64)
        # Bit manipulation
        'ext', 'ins',  # extract/insert bit field (MIPS32 R2)
        'dext', 'dextu', 'dextm',  # doubleword extract (MIPS64)
        'dins', 'dinsu', 'dinsm',  # doubleword insert (MIPS64)
        'wsbh',  # word swap bytes within halfwords
        'dsbh', 'dshd',  # doubleword swap bytes/halfwords (MIPS64)
        'seb', 'seh',  # sign-extend byte/halfword (MIPS32 R2)
        # Count bits
        'clz', 'clo',  # count leading zeros/ones
        'dclz', 'dclo',  # doubleword count leading zeros/ones (MIPS64)
        # Bit field
        'bitswap', 'dbitswap',  # reverse bits in each byte (MIPS R6)
    },

    InstructionType.STACK: set(),  # MIPS doesn't have dedicated stack instructions

    InstructionType.COMPARE: {
        # Set on less than
        'slt', 'sltu',  # set on less than (signed/unsigned)
        'slti', 'sltiu',  # set on less than immediate (signed/unsigned)
        'dslt', 'dsltu',  # doubleword set on less than (MIPS64, pseudo-instruction)
        # Set equal/not equal (pseudo-instructions)
        'seq', 'sne',  # set equal/not equal
        'sgt', 'sgtu',  # set greater than
        'sge', 'sgeu',  # set greater or equal
        'sle', 'sleu',  # set less or equal
    },

    InstructionType.OTHER: {
        # No operation
        'nop', 'ssnop',  # no operation, superscalar no operation
        # Breakpoint and trap
        'break', 'syscall',  # breakpoint, system call
        'teq', 'tne', 'tge', 'tgeu', 'tlt', 'tltu',  # trap on condition
        'teqi', 'tnei', 'tgei', 'tgeiu', 'tlti', 'tltiu',  # trap immediate
        # Sync
        'sync', 'synci',  # synchronize shared memory, instruction cache
        # Cache
        'cache', 'pref',  # cache operation, prefetch
        # Coprocessor operations
        'cop0', 'cop1', 'cop2', 'cop3',  # coprocessor operation
        'cfc0', 'ctc0',  # copy from/to coprocessor control
        'cfc1', 'ctc1',
        'cfc2', 'ctc2',
        'lwc0', 'swc0',  # load/store word coprocessor
        'lwc1', 'swc1',
        'lwc2', 'swc2',
        'lwc3', 'swc3',
        'ldc1', 'sdc1',  # load/store doubleword coprocessor
        'ldc2', 'sdc2',
        # Exception and interrupt
        'eret', 'deret',  # exception return, debug exception return
        'wait',  # wait for interrupt
        # TLB operations
        'tlbp', 'tlbr', 'tlbwi', 'tlbwr',  # TLB probe/read/write indexed/write random
        # Privileged
        'rfe',  # return from exception (MIPS I)
        'di', 'ei',  # disable/enable interrupts
        # Atomic operations
        'llwp', 'scwp',  # load linked word pair, store conditional word pair (MIPS R6)
        'lldp', 'scdp',  # load linked doubleword pair, store conditional doubleword pair
        # Miscellaneous
        'movci',  # move conditional (internal)
        'prefx',  # prefetch indexed
        'rdhwr',  # read hardware register
        'rdpgpr', 'wrpgpr',  # read/write previous guest privileged register
        # Floating point operations (basic set)
        'add.s', 'add.d', 'add.ps',  # FP add (single/double/paired single)
        'sub.s', 'sub.d', 'sub.ps',  # FP subtract
        'mul.s', 'mul.d', 'mul.ps',  # FP multiply
        'div.s', 'div.d', 'div.ps',  # FP divide
        'sqrt.s', 'sqrt.d',  # FP square root
        'abs.s', 'abs.d', 'abs.ps',  # FP absolute value
        'neg.s', 'neg.d', 'neg.ps',  # FP negate
        'mov.s', 'mov.d', 'mov.ps',  # FP move
        # FP compare
        'c.f.s', 'c.f.d', 'c.f.ps',  # compare false
        'c.un.s', 'c.un.d', 'c.un.ps',  # compare unordered
        'c.eq.s', 'c.eq.d', 'c.eq.ps',  # compare equal
        'c.ueq.s', 'c.ueq.d', 'c.ueq.ps',  # compare unordered equal
        'c.olt.s', 'c.olt.d', 'c.olt.ps',  # compare ordered less than
        'c.ult.s', 'c.ult.d', 'c.ult.ps',  # compare unordered less than
        'c.ole.s', 'c.ole.d', 'c.ole.ps',  # compare ordered less or equal
        'c.ule.s', 'c.ule.d', 'c.ule.ps',  # compare unordered less or equal
        'c.sf.s', 'c.sf.d', 'c.sf.ps',  # compare signaling false
        'c.ngle.s', 'c.ngle.d', 'c.ngle.ps',  # compare not greater or less or equal
        'c.seq.s', 'c.seq.d', 'c.seq.ps',  # compare signaling equal
        'c.ngl.s', 'c.ngl.d', 'c.ngl.ps',  # compare not greater or less
        'c.lt.s', 'c.lt.d', 'c.lt.ps',  # compare less than
        'c.nge.s', 'c.nge.d', 'c.nge.ps',  # compare not greater or equal
        'c.le.s', 'c.le.d', 'c.le.ps',  # compare less or equal
        'c.ngt.s', 'c.ngt.d', 'c.ngt.ps',  # compare not greater
        # FP convert
        'cvt.s.d', 'cvt.s.w', 'cvt.s.l',  # convert to single
        'cvt.d.s', 'cvt.d.w', 'cvt.d.l',  # convert to double
        'cvt.w.s', 'cvt.w.d',  # convert to word
        'cvt.l.s', 'cvt.l.d',  # convert to long
        'cvt.ps.s',  # convert to paired single
        'cvt.s.pl', 'cvt.s.pu',  # convert from paired single (lower/upper)
        # FP round/truncate/ceiling/floor
        'round.w.s', 'round.w.d', 'round.l.s', 'round.l.d',
        'trunc.w.s', 'trunc.w.d', 'trunc.l.s', 'trunc.l.d',
        'ceil.w.s', 'ceil.w.d', 'ceil.l.s', 'ceil.l.d',
        'floor.w.s', 'floor.w.d', 'floor.l.s', 'floor.l.d',
        # FP conditional move
        'movf.s', 'movf.d', 'movf.ps',  # move if FP false
        'movt.s', 'movt.d', 'movt.ps',  # move if FP true
        'movn.s', 'movn.d', 'movn.ps',  # move if not zero
        'movz.s', 'movz.d', 'movz.ps',  # move if zero
        # FP misc
        'recip.s', 'recip.d',  # reciprocal approximation
        'rsqrt.s', 'rsqrt.d',  # reciprocal square root approximation
        'madd.s', 'madd.d', 'madd.ps',  # multiply-add
        'msub.s', 'msub.d', 'msub.ps',  # multiply-subtract
        'nmadd.s', 'nmadd.d', 'nmadd.ps',  # negative multiply-add
        'nmsub.s', 'nmsub.d', 'nmsub.ps',  # negative multiply-subtract
        # Load/Store FP
        'sdc1',  # load/store word/double coprocessor 1
        'luxc1', 'suxc1',  # load/store doubleword FP indexed unaligned
        'ldxc1', 'sdxc1',  # load/store doubleword FP indexed
        'lwxc1', 'swxc1',  # load/store word FP indexed
    },
}


def get_instruction_type(mnemonic: str) -> InstructionType:
    """Get the instruction type for a given MIPS mnemonic.
    
    Args:
        mnemonic: The instruction mnemonic (lowercase).
    
    Returns:
        The InstructionType for this mnemonic.
    """
    mnemonic = mnemonic.lower().strip()

    # Check main instruction categories
    for instr_type, instructions in MIPS_INSTRUCTIONS.items():
        if mnemonic in instructions:
            return instr_type

    return InstructionType.OTHER


def is_branch_likely(mnemonic: str) -> bool:
    """Check if a mnemonic is a branch likely instruction.
    
    Branch likely instructions are deprecated but still used in older code.
    
    Args:
        mnemonic: The instruction mnemonic (lowercase).
    
    Returns:
        True if this is a branch likely instruction.
    """
    mnemonic = mnemonic.lower().strip()
    return mnemonic.endswith('l') and mnemonic[:-1] in {
        'beq', 'bne', 'bgtz', 'blez', 'bltz', 'bgez',
        'bc1f', 'bc1t',
    }


def is_pseudo_instruction(mnemonic: str) -> bool:
    """Check if a mnemonic is a pseudo-instruction.
    
    Pseudo-instructions are assembler conveniences that map to real instructions.
    
    Args:
        mnemonic: The instruction mnemonic (lowercase).
    
    Returns:
        True if this is a pseudo-instruction.
    """
    mnemonic = mnemonic.lower().strip()

    pseudo_instructions = {
        'move', 'li', 'la', 'b', 'bal', 'not',
        'neg', 'negu', 'abs',
        'seq', 'sne', 'sgt', 'sgtu', 'sge', 'sgeu', 'sle', 'sleu',
        'dslt', 'dsltu',
    }

    return mnemonic in pseudo_instructions


def is_fp_instruction(mnemonic: str) -> bool:
    """Check if a mnemonic is a floating-point instruction.
    
    Args:
        mnemonic: The instruction mnemonic (lowercase).
    
    Returns:
        True if this is a floating-point instruction.
    """
    mnemonic = mnemonic.lower().strip()

    # FP instructions have format suffixes: .s (single), .d (double), .ps (paired single)
    return ('.s' in mnemonic or '.d' in mnemonic or '.ps' in mnemonic or
            'c.f.' in mnemonic or 'c.un.' in mnemonic or 'c.eq.' in mnemonic or
            'c.ueq.' in mnemonic or 'c.olt.' in mnemonic or 'c.ult.' in mnemonic or
            'c.ole.' in mnemonic or 'c.ule.' in mnemonic or 'c.sf.' in mnemonic or
            'c.ngle.' in mnemonic or 'c.seq.' in mnemonic or 'c.ngl.' in mnemonic or
            'c.lt.' in mnemonic or 'c.nge.' in mnemonic or 'c.le.' in mnemonic or
            'c.ngt.' in mnemonic)


def is_coprocessor_instruction(mnemonic: str) -> bool:
    """Check if a mnemonic is a coprocessor instruction.
    
    Args:
        mnemonic: The instruction mnemonic (lowercase).
    
    Returns:
        True if this is a coprocessor instruction.
    """
    mnemonic = mnemonic.lower().strip()

    # Coprocessor instructions reference cop0, cop1, cop2, cop3
    # or have specific patterns like mfc0, mtc0, lwc1, etc.
    coprocessor_prefixes = ['cop', 'mfc', 'mtc', 'cfc', 'ctc', 'lwc', 'swc', 'ldc', 'sdc']

    for prefix in coprocessor_prefixes:
        if mnemonic.startswith(prefix):
            return True

    return False
