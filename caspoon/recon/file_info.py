"""File information reconnaissance module."""

import logging
import os

from elftools.elf.elffile import ELFFile

from ..core.models import ExecutableReport

logger = logging.getLogger(__name__)

# Architecture mapping from ELF e_machine string values (as returned by pyelftools) to human-readable names
ARCH_MAP: dict[str, str] = {
    "EM_X86_64": "x86_64",
    "EM_386": "x86",
    "EM_ARM": "ARM",
    "EM_AARCH64": "ARM64",
    "EM_MIPS": "MIPS",
    "EM_PPC": "PowerPC",
    "EM_PPC64": "PowerPC64",
    "EM_RISCV": "RISC-V",
    "EM_S390": "S390",
    "EM_SH": "SuperH",
    "EM_IA_64": "IA-64",
}


class FileInfoRecon:
    """Extracts basic file information using pyelftools.

    Analyzes the executable to determine architecture, bit width,
    file type, and whether debug symbols are stripped.
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
            with open(path, "rb") as f:
                try:
                    elffile = ELFFile(f)
                except Exception as e:
                    logger.warning(f"Not an ELF file or invalid ELF: {path} - {e}")
                    report.file_type = "Not an ELF file"
                    return report

                # Detect architecture
                e_machine = elffile.header["e_machine"]
                report.arch = ARCH_MAP.get(e_machine, "Unknown")

                # Detect bit width
                elfclass = elffile.elfclass
                report.bits = 64 if elfclass == 64 else 32 if elfclass == 32 else None

                # Detect endianness
                endian_str = "LSB" if elffile.little_endian else "MSB"

                # Detect file type
                e_type = elffile.header["e_type"]
                if e_type == "ET_EXEC":
                    type_str = "executable"
                elif e_type == "ET_DYN":
                    type_str = "shared object"
                elif e_type == "ET_REL":
                    type_str = "relocatable"
                elif e_type == "ET_CORE":
                    type_str = "core dump"
                else:
                    type_str = "unknown type"

                # Build descriptive file_type string
                arch_str = report.arch if report.arch != "Unknown" else f"machine {e_machine}"
                report.file_type = f"ELF {report.bits}-bit {endian_str} {type_str}, {arch_str}"

                # Check if stripped (no symbol table)
                report.stripped = elffile.get_section_by_name(".symtab") is None

        except Exception as e:
            logger.error(f"Unexpected error in FileInfoRecon: {e}")
            report.file_type = f"Error: {str(e)}"

        return report
