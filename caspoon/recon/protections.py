"""Security protections reconnaissance module."""

import logging

from elftools.elf.constants import P_FLAGS
from elftools.elf.dynamic import DynamicSection
from elftools.elf.elffile import ELFFile

from ..core.models import ExecutableReport, ProtectionInfo

logger = logging.getLogger(__name__)


class ProtectionsRecon:
    """Analyzes security protections using pyelftools.

    Detects security features including PIE, NX, stack canary, and RELRO.
    """

    name = "protections"

    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        """Run protections reconnaissance.

        Args:
            path: Path to the executable file
            report: ExecutableReport to enrich with protection information

        Returns:
            Updated ExecutableReport with protection information
        """
        pi = ProtectionInfo()

        try:
            with open(path, "rb") as f:
                try:
                    elffile = ELFFile(f)
                except Exception as e:
                    logger.warning(f"Not an ELF file or invalid ELF: {path} - {e}")
                    pi.relro = "not_elf"
                    report.protections = pi
                    return report

                # Detect PIE: ET_DYN type indicates position independent
                pi.pie = elffile.header["e_type"] == "ET_DYN"

                # Detect NX: Check PT_GNU_STACK segment for execute permission
                pi.nx = self._check_nx(elffile)

                # Detect Stack Canary: Look for __stack_chk_fail symbol
                pi.canary = self._check_canary(elffile)

                # Detect RELRO: Check for PT_GNU_RELRO segment and DT_BIND_NOW
                pi.relro = self._check_relro(elffile)

        except Exception as e:
            logger.error(f"Unexpected error in ProtectionsRecon: {e}")
            pi.relro = f"error: {str(e)}"

        report.protections = pi
        return report

    def _check_nx(self, elffile: ELFFile) -> bool:
        """Check if NX (No-Execute) protection is enabled.

        Args:
            elffile: Parsed ELF file

        Returns:
            True if NX is enabled, False otherwise
        """
        # Look for PT_GNU_STACK segment
        for segment in elffile.iter_segments():
            if segment["p_type"] == "PT_GNU_STACK":
                # Check if executable flag is NOT set
                flags = segment["p_flags"]
                return not (flags & P_FLAGS.PF_X)

        # If no PT_GNU_STACK segment found, NX is enabled by default on modern systems
        return True

    def _check_canary(self, elffile: ELFFile) -> bool:
        """Check if stack canary protection is enabled.

        Args:
            elffile: Parsed ELF file

        Returns:
            True if stack canary is present, False otherwise
        """
        # Check dynamic symbol table for __stack_chk_fail
        dynsym = elffile.get_section_by_name(".dynsym")
        if dynsym:
            for symbol in dynsym.iter_symbols():
                if symbol.name == "__stack_chk_fail":
                    return True

        return False

    def _check_relro(self, elffile: ELFFile) -> str:
        """Check RELRO (Relocation Read-Only) protection level.

        Args:
            elffile: Parsed ELF file

        Returns:
            "full", "partial", or "none"
        """
        has_gnu_relro = False
        has_bind_now = False

        # Check for PT_GNU_RELRO segment
        for segment in elffile.iter_segments():
            if segment["p_type"] == "PT_GNU_RELRO":
                has_gnu_relro = True
                break

        # Check for DT_BIND_NOW or DT_FLAGS with DF_BIND_NOW bit in .dynamic section
        DF_BIND_NOW = 0x8
        for section in elffile.iter_sections():
            if isinstance(section, DynamicSection):
                for tag in section.iter_tags():
                    if tag.entry.d_tag == "DT_BIND_NOW":
                        has_bind_now = True
                        break
                    if tag.entry.d_tag == "DT_FLAGS" and (tag.entry.d_val & DF_BIND_NOW):
                        has_bind_now = True
                        break
                if has_bind_now:
                    break

        # Determine RELRO level
        if has_gnu_relro and has_bind_now:
            return "full"
        elif has_gnu_relro:
            return "partial"
        else:
            return "none"
