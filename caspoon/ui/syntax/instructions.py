"""Instruction classification for x86/x64 assembly mnemonics."""

from .schemes import InstructionType

X86_64_INSTRUCTIONS: dict[InstructionType, set[str]] = {
    InstructionType.JUMP: {
        'jmp', 'jmpq', 'jmpl', 'jmpw',
        'je', 'jz', 'jne', 'jnz',
        'jg', 'jnle', 'jge', 'jnl',
        'jl', 'jnge', 'jle', 'jng',
        'ja', 'jnbe', 'jae', 'jnb', 'jnc',
        'jb', 'jnae', 'jc', 'jbe', 'jna',
        'jo', 'jno', 'js', 'jns',
        'jp', 'jpe', 'jnp', 'jpo',
        'jcxz', 'jecxz', 'jrcxz',
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
        'mov', 'movq', 'movl', 'movw', 'movb',
        'movzx', 'movzb', 'movzw', 'movzl', 'movzq',
        'movsx', 'movsxd', 'movsbq', 'movswq', 'movslq',
        'lea', 'leaq', 'leal', 'leaw',
        'xchg', 'xchgq', 'xchgl', 'xchgw', 'xchgb',
        'cmove', 'cmovz', 'cmovne', 'cmovnz',
        'cmovg', 'cmovge', 'cmovl', 'cmovle',
        'cmova', 'cmovae', 'cmovb', 'cmovbe',
        'cmovo', 'cmovno', 'cmovs', 'cmovns',
        'cmovp', 'cmovnp',
        'sete', 'setz', 'setne', 'setnz',
        'setg', 'setge', 'setl', 'setle',
        'seta', 'setae', 'setb', 'setbe',
        'seto', 'setno', 'sets', 'setns',
        'setp', 'setnp',
    },
    InstructionType.ARITHMETIC: {
        'add', 'addq', 'addl', 'addw', 'addb',
        'adc', 'adcq', 'adcl', 'adcw', 'adcb',
        'sub', 'subq', 'subl', 'subw', 'subb',
        'sbb', 'sbbq', 'sbbl', 'sbbw', 'sbbb',
        'mul', 'mulq', 'mull', 'mulw', 'mulb',
        'imul', 'imulq', 'imull', 'imulw', 'imulb',
        'div', 'divq', 'divl', 'divw', 'divb',
        'idiv', 'idivq', 'idivl', 'idivw', 'idivb',
        'inc', 'incq', 'incl', 'incw', 'incb',
        'dec', 'decq', 'decl', 'decw', 'decb',
        'neg', 'negq', 'negl', 'negw', 'negb',
        'cbw', 'cwde', 'cdqe', 'cwd', 'cdq', 'cqo',
    },
    InstructionType.LOGIC: {
        'and', 'andq', 'andl', 'andw', 'andb',
        'or', 'orq', 'orl', 'orw', 'orb',
        'xor', 'xorq', 'xorl', 'xorw', 'xorb',
        'not', 'notq', 'notl', 'notw', 'notb',
        'shl', 'shlq', 'shll', 'shlw', 'shlb',
        'sal', 'salq', 'sall', 'salw', 'salb',
        'shr', 'shrq', 'shrl', 'shrw', 'shrb',
        'sar', 'sarq', 'sarl', 'sarw', 'sarb',
        'rol', 'rolq', 'roll', 'rolw', 'rolb',
        'ror', 'rorq', 'rorl', 'rorw', 'rorb',
        'rcl', 'rclq', 'rcll', 'rclw', 'rclb',
        'rcr', 'rcrq', 'rcrl', 'rcrw', 'rcrb',
        'bt', 'btq', 'btl', 'btw',
        'bts', 'btsq', 'btsl', 'btsw',
        'btr', 'btrq', 'btrl', 'btrw',
        'btc', 'btcq', 'btcl', 'btcw',
        'bsf', 'bsfq', 'bsfl', 'bsfw',
        'bsr', 'bsrq', 'bsrl', 'bsrw',
        'bswap', 'bswapq', 'bswapl',
    },
    InstructionType.STACK: {
        'push', 'pushq', 'pushl', 'pushw', 'pushb',
        'pop', 'popq', 'popl', 'popw', 'popb',
        'pusha', 'pushad', 'popa', 'popad',
        'pushf', 'pushfq', 'pushfd', 'pushfw',
        'popf', 'popfq', 'popfd', 'popfw',
        'enter', 'enterq', 'enterl',
        'leave', 'leaveq', 'leavel',
    },
    InstructionType.COMPARE: {
        'cmp', 'cmpq', 'cmpl', 'cmpw', 'cmpb',
        'test', 'testq', 'testl', 'testw', 'testb',
    },
    InstructionType.OTHER: {
        'nop', 'nopq', 'nopl', 'nopw',
        'ud2', 'ud2a', 'ud2b',
        'cpuid', 'rdtsc', 'rdtscp', 'rdpmc',
        'rdmsr', 'wrmsr',
        'clc', 'stc', 'cmc', 'cld', 'std', 'cli', 'sti',
        'lds', 'les', 'lfs', 'lgs', 'lss',
        'lgdt', 'sgdt', 'lidt', 'sidt',
        'lldt', 'sldt', 'ltr', 'str',
        'xlat', 'xlatb', 'bound',
        'int', 'int3', 'into',
        'syscall', 'sysret', 'sysenter', 'sysexit',
        'hlt',
        'lfence', 'sfence', 'mfence',
        'lock',
        'monitor', 'mwait',
    },
}


def get_instruction_type(mnemonic: str) -> InstructionType:
    """Return the InstructionType for a given mnemonic string.

    Args:
        mnemonic: Instruction mnemonic (case-insensitive).

    Returns:
        Matching InstructionType, or InstructionType.OTHER if unrecognised.
    """
    mnemonic = mnemonic.lower().strip()
    for instr_type, mnemonics in X86_64_INSTRUCTIONS.items():
        if mnemonic in mnemonics:
            return instr_type
    return InstructionType.OTHER
