"""Security protections reconnaissance module."""

import logging

from elftools.elf.elffile import ELFFile

from ..core.models import ExecutableReport, ProtectionInfo

logger = logging.getLogger(__name__)

# Magic bytes for format detection
_ELF_MAGIC = b"\x7fELF"
_PE_MAGIC = b"MZ"

# PE DLL characteristics flags (MSDN IMAGE_DLLCHARACTERISTICS_*)
_PE_DYNAMIC_BASE = 0x0040  # ASLR / PIE equivalent
_PE_NX_COMPAT = 0x0100     # NX / DEP

# ELF program header flags
_PF_X = 0x1  # Execute permission


def _read_magic(path: str, n: int = 4) -> bytes:
    """Read the first n bytes of a file to identify its format."""
    with open(path, "rb") as f:
        return f.read(n)


def _detect_elf_protections(path: str) -> ProtectionInfo:
    """Detect security protections in an ELF binary using pyelftools.

    Checks:
      - PIE: ET_DYN object type indicates position-independent execution
      - NX: GNU_STACK segment present without the execute flag
      - Stack canary: presence of __stack_chk_fail / __stack_chk_guard symbol
      - RELRO: PT_GNU_RELRO segment; full when combined with DT_BIND_NOW / DF_BIND_NOW
    """
    pi = ProtectionInfo()

    with open(path, "rb") as f:
        elf = ELFFile(f)

        # --- PIE ---
        pi.pie = elf.header.e_type == "ET_DYN"

        # --- NX ---
        # NX is enabled when a GNU_STACK segment exists and lacks the execute flag.
        pi.nx = False
        for seg in elf.iter_segments():
            if seg.header.p_type == "PT_GNU_STACK":
                pi.nx = not bool(seg.header.p_flags & _PF_X)
                break

        # --- Stack canary ---
        pi.canary = False
        dynsym = elf.get_section_by_name(".dynsym")
        if dynsym:
            canary_symbols = {"__stack_chk_fail", "__stack_chk_guard"}
            for sym in dynsym.iter_symbols():
                if sym.name in canary_symbols:
                    pi.canary = True
                    break

        # --- RELRO ---
        has_relro = any(
            seg.header.p_type == "PT_GNU_RELRO" for seg in elf.iter_segments()
        )

        if has_relro:
            has_bind_now = False
            dynamic = elf.get_section_by_name(".dynamic")
            if dynamic:
                for tag in dynamic.iter_tags():
                    if tag.entry.d_tag == "DT_BIND_NOW":
                        has_bind_now = True
                        break
                    # DT_FLAGS with DF_BIND_NOW (0x8) also implies full RELRO
                    if tag.entry.d_tag == "DT_FLAGS" and (tag.entry.d_val & 0x8):
                        has_bind_now = True
                        break
            pi.relro = "full" if has_bind_now else "partial"
        else:
            pi.relro = "none"

    return pi


def _detect_pe_protections(path: str) -> ProtectionInfo:
    """Detect security protections in a PE binary.

    Uses pefile when available; marks protections as unavailable otherwise.
    Stack canary and RELRO are ELF-specific and reported as N/A for PE.
    """
    pi = ProtectionInfo()

    try:
        import pefile  # optional dependency

        pe = pefile.PE(path)
        chars = pe.OPTIONAL_HEADER.DllCharacteristics
        pi.pie = bool(chars & _PE_DYNAMIC_BASE)
        pi.nx = bool(chars & _PE_NX_COMPAT)
        pi.canary = False
        pi.relro = "N/A"

    except ImportError:
        logger.warning(
            "pefile not installed; PE protection details unavailable. "
            "Run: pip install pefile"
        )
        pi.relro = "N/A (install pefile for PE support)"

    return pi


class ProtectionsRecon:
    """Analyzes security protections in ELF and PE binaries.

    Uses pyelftools for ELF binaries and pefile (when available) for PE
    binaries. No external system tools required.
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
        try:
            magic = _read_magic(path)
        except OSError as e:
            logger.error(f"Could not read file for protections check: {e}")
            report.protections = ProtectionInfo(relro=f"Error: {e}")
            return report

        try:
            if magic[:4] == _ELF_MAGIC:
                report.protections = _detect_elf_protections(path)
            elif magic[:2] == _PE_MAGIC:
                report.protections = _detect_pe_protections(path)
            else:
                logger.warning(f"Unsupported format for protections check: {path}")
                report.protections = ProtectionInfo(relro="N/A (unsupported format)")

        except Exception as e:
            logger.error(f"Unexpected error in ProtectionsRecon: {e}")
            report.protections = ProtectionInfo(relro=f"Error: {str(e)}")

        return report
