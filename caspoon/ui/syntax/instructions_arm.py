"""Comprehensive instruction database for ARM/ARM64 assembly.

This module provides detailed instruction classifications for ARM and ARM64
assembly code, organized by instruction type for syntax highlighting
and analysis purposes.
"""

from .schemes import InstructionType

# Comprehensive ARM/ARM64 instruction database
# Maps instruction types to sets of instruction mnemonics

ARM_INSTRUCTIONS = {
    InstructionType.JUMP: {
        # Unconditional branches (ARM32)
        'b', 'bx',
        # Conditional branches (ARM32) - condition suffixes
        'beq', 'bne', 'bcs', 'bhs', 'bcc', 'blo',
        'bmi', 'bpl', 'bvs', 'bvc',
        'bhi', 'bls', 'bge', 'blt', 'bgt', 'ble', 'bal',
        # ARM64 branches
        'br', 'b.eq', 'b.ne', 'b.cs', 'b.hs', 'b.cc', 'b.lo',
        'b.mi', 'b.pl', 'b.vs', 'b.vc',
        'b.hi', 'b.ls', 'b.ge', 'b.lt', 'b.gt', 'b.le', 'b.al',
        # Compare and branch (ARM64)
        'cbz', 'cbnz', 'tbz', 'tbnz',
    },

    InstructionType.CALL: {
        # Branch with link (function calls)
        'bl', 'blx', 'blr',  # bl/blx for ARM32, blr for ARM64
    },

    InstructionType.RETURN: {
        # Return instructions
        'ret',  # ARM64
        'bx lr',  # ARM32 common return pattern (will match 'bx' in JUMP, but this is ok)
    },

    InstructionType.MOVE: {
        # Basic move operations
        'mov', 'movw', 'movt', 'mvn',  # move, move wide, move top, move not
        # ARM64 moves
        'movz', 'movk', 'movn',  # move with zero/keep/not
        # Conditional moves
        'moveq', 'movne', 'movcs', 'movhs', 'movcc', 'movlo',
        'movmi', 'movpl', 'movvs', 'movvc',
        'movhi', 'movls', 'movge', 'movlt', 'movgt', 'movle',
        # Select (ARM64)
        'csel', 'csinc', 'csinv', 'csneg',  # conditional select variants
        # Exchange
        'swp', 'swpb',  # swap
        # Load/Store operations (data movement)
        # Single load/store
        'ldr', 'str',  # load/store register
        'ldrb', 'strb',  # byte
        'ldrh', 'strh',  # halfword
        'ldrsb', 'ldrsh', 'ldrsw',  # signed byte/halfword/word
        # ARM64 load/store
        'ldar', 'stlr',  # acquire/release
        'ldarb', 'stlrb', 'ldarh', 'stlrh',
        'ldaxr', 'stlxr',  # exclusive
        'ldxr', 'stxr', 'ldxrb', 'stxrb', 'ldxrh', 'stxrh',
        # Address calculation
        'adr', 'adrp',  # form PC-relative address
        'adrl',  # pseudo-instruction for ADR with larger range
        # Conditional loads/stores
        'ldreq', 'ldrne', 'ldrcs', 'ldrhs', 'ldrcc', 'ldrlo',
        'ldrmi', 'ldrpl', 'ldrvs', 'ldrvc',
        'ldrhi', 'ldrls', 'ldrge', 'ldrlt', 'ldrgt', 'ldrle',
        'streq', 'strne', 'strcs', 'strhs', 'strcc', 'strlo',
        'strmi', 'strpl', 'strvs', 'strvc',
        'strhi', 'strls', 'strge', 'strlt', 'strgt', 'strle',
    },

    InstructionType.ARITHMETIC: {
        # Addition
        'add', 'adc', 'addw', 'adds', 'adcs',  # add, add with carry
        # Subtraction
        'sub', 'sbc', 'subw', 'subs', 'sbcs', 'rsb', 'rsc',  # subtract, reverse subtract
        # Multiplication
        'mul', 'mla', 'mls',  # multiply, multiply accumulate
        'smull', 'umull', 'smlal', 'umlal',  # long multiply
        'smulh', 'umulh',  # high multiply (ARM64)
        'madd', 'msub',  # multiply add/sub (ARM64)
        # Division (ARM64 and some ARM32)
        'sdiv', 'udiv',
        # Multiply-accumulate
        'umlal',
        # Negate
        'neg', 'negs', 'ngc', 'ngcs',
        # Absolute
        'abs',
        # Conditional arithmetic
        'addeq', 'addne', 'addcs', 'addhs', 'addcc', 'addlo',
        'addmi', 'addpl', 'addvs', 'addvc',
        'addhi', 'addls', 'addge', 'addlt', 'addgt', 'addle',
        'subeq', 'subne', 'subcs', 'subhs', 'subcc', 'sublo',
        'submi', 'subpl', 'subvs', 'subvc',
        'subhi', 'subls', 'subge', 'sublt', 'subgt', 'suble',
    },

    InstructionType.LOGIC: {
        # Logical operations
        'and', 'orr', 'eor', 'bic', 'orn', 'eon',  # and, or, xor, bit clear
        'ands', 'orrs', 'eors', 'bics',  # with status update
        # Bitwise NOT
        'mvn', 'mvns',
        # Shift operations
        'lsl', 'lsr', 'asr', 'ror', 'rrx',  # logical/arithmetic shift, rotate
        'lsls', 'lsrs', 'asrs', 'rors',  # with status update
        # ARM64 shifts
        'lslv', 'lsrv', 'asrv', 'rorv',  # variable shifts
        # Bit field operations
        'bfi', 'bfc', 'bfm', 'bfxil',  # bit field insert/clear/move
        'sbfm', 'ubfm', 'sbfiz', 'ubfiz', 'sbfx', 'ubfx',  # signed/unsigned bit field
        # Bit manipulation
        'rbit', 'rev', 'rev16', 'rev32',  # reverse bits/bytes
        'clz', 'cls',  # count leading zeros/signs
        # Conditional logical operations
        'andeq', 'andne', 'andcs', 'andhs', 'andcc', 'andlo',
        'andmi', 'andpl', 'andvs', 'andvc',
        'andhi', 'andls', 'andge', 'andlt', 'andgt', 'andle',
        'orreq', 'orrne', 'orrcs', 'orrhs', 'orrcc', 'orrlo',
        'orrmi', 'orrpl', 'orrvs', 'orrvc',
        'orrhi', 'orrls', 'orrge', 'orrlt', 'orrgt', 'orrle',
        'eoreq', 'eorne', 'eorcs', 'eorhs', 'eorcc', 'eorlo',
        'eormi', 'eorpl', 'eorvs', 'eorvc',
        'eorhi', 'eorls', 'eorge', 'eorlt', 'eorgt', 'eorle',
    },

    InstructionType.STACK: {
        # Push and pop (ARM32)
        'push', 'pop',
        # Load/Store multiple (used for stack operations)
        'stm', 'stmia', 'stmib', 'stmda', 'stmdb',  # store multiple
        'ldm', 'ldmia', 'ldmib', 'ldmda', 'ldmdb',  # load multiple
        'stmfd', 'stmfa', 'stmed', 'stmea',  # store multiple (full/empty, descending/ascending)
        'ldmfd', 'ldmfa', 'ldmed', 'ldmea',  # load multiple
        # ARM64 stack operations
        'stp', 'ldp',  # store/load pair (commonly used for stack)
    },

    InstructionType.COMPARE: {
        # Compare operations
        'cmp', 'cmn',  # compare, compare negative
        'tst', 'teq',  # test bits, test equivalence
        # ARM64 compare
        'ccmn', 'ccmp',  # conditional compare
    },

    InstructionType.OTHER: {
        # No operation
        'nop',
        # Breakpoint
        'bkpt', 'brk',  # breakpoint (ARM32/ARM64)
        # Hints
        'yield', 'wfe', 'wfi', 'sev', 'sevl',  # wait for event, etc.
        # Barriers
        'dsb', 'dmb', 'isb',  # data/instruction synchronization barriers
        # System register access (ARM64)
        'mrs', 'msr',  # move to/from system register
        # Coprocessor operations
        'mcr', 'mrc', 'mcrr', 'mrrc',  # ARM32 coprocessor
        'cdp', 'ldc', 'stc',
        # Undefined instruction
        'udf', 'und',
        # Supervisor call
        'svc', 'swi',  # supervisor call (software interrupt)
        # Hint instructions
        'pld', 'pldw', 'pli',  # preload
        # Cache operations
        'ic', 'dc', 'at', 'tlbi',  # ARM64 cache/TLB operations
        # Atomic operations (ARM64)
        'ldadd', 'ldclr', 'ldeor', 'ldset',  # atomic memory operations
        'ldaddh', 'ldclrh', 'ldeorh', 'ldseth',
        'ldaddb', 'ldclrb', 'ldeorb', 'ldsetb',
        'stadd', 'stclr', 'steor', 'stset',
        'staddh', 'stclrh', 'steorh', 'stseth',
        'staddb', 'stclrb', 'steorb', 'stsetb',
        'cas', 'casa', 'casl', 'casal',  # compare and swap
        'cash', 'casah', 'caslh', 'casalh',
        'casb', 'casab', 'caslb', 'casalb',
        # Floating point and SIMD (NEON/Advanced SIMD)
        # Data movement
        'fmov', 'vmov', 'vdup',
        # Arithmetic
        'fadd', 'fsub', 'fmul', 'fdiv', 'fsqrt',
        'vadd', 'vsub', 'vmul', 'vdiv', 'vsqrt',
        # Compare
        'fcmp', 'fcmpe', 'vcmp', 'vcmpe',
        # Convert
        'fcvt', 'fcvtas', 'fcvtms', 'fcvtns', 'fcvtps', 'fcvtzs', 'fcvtzu',
        'scvtf', 'ucvtf',
        'vcvt',
        # SIMD operations
        'vld1', 'vld2', 'vld3', 'vld4',  # vector load
        'vst1', 'vst2', 'vst3', 'vst4',  # vector store
        'vext', 'vrev', 'vtrn', 'vuzp', 'vzip',  # vector rearrange
        # Advanced SIMD arithmetic
        'vabs', 'vneg', 'vmax', 'vmin',
        'vpadd', 'vpmax', 'vpmin',
        'vmla', 'vmls', 'vmlal', 'vmlsl',
        'vqadd', 'vqsub',  # saturating add/sub
        # Miscellaneous
        'it', 'ite', 'itt', 'ittt', 'itttt',  # if-then (Thumb)
        'itee', 'itte', 'ittee', 'ittte', 'itete', 'itett',
        'iteee', 'iteet', 'ittet',
    },
}


def get_instruction_type(mnemonic: str) -> InstructionType:
    """Get the instruction type for a given ARM mnemonic.
    
    Args:
        mnemonic: The instruction mnemonic (lowercase).
    
    Returns:
        The InstructionType for this mnemonic.
    """
    mnemonic = mnemonic.lower().strip()

    # Check main instruction categories
    for instr_type, instructions in ARM_INSTRUCTIONS.items():
        if mnemonic in instructions:
            return instr_type

    return InstructionType.OTHER


def is_conditional_instruction(mnemonic: str) -> bool:
    """Check if a mnemonic is a conditional instruction.
    
    ARM instructions can have condition suffixes like eq, ne, cs, etc.
    
    Args:
        mnemonic: The instruction mnemonic (lowercase).
    
    Returns:
        True if this instruction has a condition suffix.
    """
    mnemonic = mnemonic.lower().strip()

    # Common ARM condition suffixes
    conditions = ['eq', 'ne', 'cs', 'hs', 'cc', 'lo', 'mi', 'pl',
                  'vs', 'vc', 'hi', 'ls', 'ge', 'lt', 'gt', 'le', 'al']

    for cond in conditions:
        if mnemonic.endswith(cond):
            return True

    return False


def is_thumb_instruction(mnemonic: str) -> bool:
    """Check if a mnemonic is a Thumb-specific instruction.
    
    Args:
        mnemonic: The instruction mnemonic (lowercase).
    
    Returns:
        True if this is a Thumb-specific instruction.
    """
    mnemonic = mnemonic.lower().strip()

    # IT (if-then) instructions are Thumb-specific
    thumb_instructions = {
        'it', 'ite', 'itt', 'ittt', 'itttt',
        'itee', 'itte', 'ittee', 'ittte', 'itete', 'itett',
        'iteee', 'iteet', 'ittet',
    }

    return mnemonic in thumb_instructions


def is_neon_instruction(mnemonic: str) -> bool:
    """Check if a mnemonic is a NEON/Advanced SIMD instruction.
    
    Args:
        mnemonic: The instruction mnemonic (lowercase).
    
    Returns:
        True if this is a NEON instruction.
    """
    mnemonic = mnemonic.lower().strip()

    # NEON instructions typically start with 'v'
    return mnemonic.startswith('v') and len(mnemonic) > 1
