"""File information reconnaissance module."""

import logging
import os

from elftools.elf.elffile import ELFFile

from ..core.models import ExecutableReport

logger = logging.getLogger(__name__)

# ELF magic bytes
_ELF_MAGIC = b"\x7fELF"

# PE magic bytes
_PE_MAGIC = b"MZ"

# Mach-O magic bytes (big-endian and little-endian, 32-bit and 64-bit)
_MACHO_MAGIC = {
    b"\xfe\xed\xfa\xce",  # 32-bit big-endian
    b"\xfe\xed\xfa\xcf",  # 64-bit big-endian
    b"\xce\xfa\xed\xfe",  # 32-bit little-endian
    b"\xcf\xfa\xed\xfe",  # 64-bit little-endian
}

# pyelftools get_machine_arch() → normalized architecture name
_ELF_ARCH_MAP: dict[str, str] = {
    "x86": "x86",
    "x64": "x86_64",
    "ARM": "ARM",
    "AArch64": "ARM64",
    "MIPS": "MIPS",
    "PowerPC": "PowerPC",
    "PowerPC64": "PowerPC64",
    "S390": "S390",
    "SPARC": "SPARC",
}

# PE machine type constants → (architecture name, bit width)
_PE_MACHINE_MAP: dict[int, tuple[str, int]] = {
    0x014C: ("x86", 32),
    0x8664: ("x86_64", 64),
    0xAA64: ("ARM64", 64),
    0x01C4: ("ARM", 32),
}

# ELF e_type → human-readable object type
_ELF_TYPE_MAP: dict[str, str] = {
    "ET_EXEC": "executable",
    "ET_DYN": "shared object",
    "ET_REL": "relocatable object",
    "ET_CORE": "core dump",
}


def _read_magic(path: str, n: int = 4) -> bytes:
    """Read the first n bytes of a file to identify its format."""
    with open(path, "rb") as f:
        return f.read(n)


def _analyze_elf(path: str, report: ExecutableReport) -> ExecutableReport:
    """Populate report fields from an ELF binary using pyelftools."""
    with open(path, "rb") as f:
        elf = ELFFile(f)

        raw_arch = elf.get_machine_arch()
        report.arch = _ELF_ARCH_MAP.get(raw_arch, raw_arch)
        report.bits = elf.elfclass

        # A binary is stripped when it has no symbol table section
        report.stripped = elf.get_section_by_name(".symtab") is None

        endian = "LSB" if elf.little_endian else "MSB"
        obj_type = _ELF_TYPE_MAP.get(elf.header.e_type, elf.header.e_type)
        report.file_type = f"ELF {elf.elfclass}-bit {endian} {obj_type}, {raw_arch}"

    return report


def _analyze_pe(path: str, report: ExecutableReport) -> ExecutableReport:
    """Populate report fields from a PE (Windows) binary.

    Uses pefile when available; falls back to limited info otherwise.
    """
    try:
        import pefile  # optional dependency

        pe = pefile.PE(path)
        arch, bits = _PE_MACHINE_MAP.get(
            pe.FILE_HEADER.Machine, ("Unknown", None)
        )
        report.arch = arch
        report.bits = bits
        report.stripped = not bool(pe.FILE_HEADER.NumberOfSymbols)
        width = f"{bits}-bit" if bits else "unknown-bit"
        report.file_type = f"PE {width} {arch} executable"

    except ImportError:
        report.arch = "Unknown"
        report.bits = None
        report.stripped = False
        report.file_type = "PE executable (install pefile for detailed info)"

    return report


def _analyze_macho(path: str, report: ExecutableReport) -> ExecutableReport:
    """Populate report fields from a Mach-O binary (basic detection only)."""
    report.file_type = "Mach-O executable"
    report.arch = "Unknown"
    report.bits = None
    report.stripped = False
    return report


class FileInfoRecon:
    """Extracts basic file information using pyelftools (and pefile when available).

    Identifies executable format from magic bytes, then uses native Python
    libraries to detect architecture, bit width, file type, and stripped status.
    No external system tools required.
    """

    name = "file_info"

    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        """Run file information reconnaissance.

        Args:
            path: Path to the executable file
            report: ExecutableReport to enrich with file information

        Returns:
            Updated ExecutableReport with file information
        """
        if not os.path.exists(path):
            logger.error(f"File not found: {path}")
            report.file_type = "Error: File not found"
            return report

        if not os.path.isfile(path):
            logger.error(f"Path is not a file: {path}")
            report.file_type = "Error: Not a file"
            return report

        try:
            magic = _read_magic(path)
        except OSError as e:
            logger.error(f"Could not read file: {e}")
            report.file_type = f"Error: {e}"
            return report

        try:
            if magic[:4] == _ELF_MAGIC:
                return _analyze_elf(path, report)
            elif magic[:2] == _PE_MAGIC:
                return _analyze_pe(path, report)
            elif magic[:4] in _MACHO_MAGIC:
                return _analyze_macho(path, report)
            else:
                report.file_type = f"Unknown format (magic: {magic.hex()})"
                report.arch = "Unknown"
                logger.warning(f"Unrecognized file format for: {path}")
                return report

        except Exception as e:
            logger.error(f"Unexpected error in FileInfoRecon: {e}")
            report.file_type = f"Error: {str(e)}"
            return report
