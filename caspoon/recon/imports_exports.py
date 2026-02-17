"""Import and export functions reconnaissance module."""

import logging
import os

from elftools.elf.elffile import ELFFile

from ..core.models import ExecutableReport

logger = logging.getLogger(__name__)

# Maximum file size to process (100 MB)
MAX_FILE_SIZE = 100 * 1024 * 1024


class ImportExportRecon:
    """Analyzes imported and exported functions using pyelftools.

    Parses ELF files to extract function imports and exports from
    the symbol tables.
    """

    name = "imports_exports"

    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        """Run imports/exports reconnaissance.

        Args:
            path: Path to the executable file
            report: ExecutableReport to enrich with imports/exports

        Returns:
            Updated ExecutableReport with imports and exports lists
        """
        # Validate file exists and check size
        if not os.path.exists(path):
            logger.error(f"File not found: {path}")
            report.raw_backend_data["imports_exports_error"] = "File not found"
            return report

        try:
            file_size = os.path.getsize(path)
            if file_size > MAX_FILE_SIZE:
                logger.warning(
                    f"File size ({file_size} bytes) exceeds limit "
                    f"({MAX_FILE_SIZE} bytes). Skipping."
                )
                report.raw_backend_data["imports_exports_error"] = "File too large"
                return report
        except OSError as e:
            logger.error(f"Error checking file size: {e}")
            report.raw_backend_data["imports_exports_error"] = str(e)
            return report

        try:
            with open(path, "rb") as f:
                try:
                    elf = ELFFile(f)
                except Exception as e:
                    logger.info(f"Not an ELF file or corrupted: {e}")
                    report.raw_backend_data["imports_exports_error"] = "Not an ELF file"
                    return report

                # Extract imports from dynamic symbol table
                dynsym = elf.get_section_by_name(".dynsym")
                if dynsym:
                    for sym in dynsym.iter_symbols():
                        if sym["st_info"]["type"] == "STT_FUNC" and sym.name:
                            # Only add non-empty function names
                            if sym.name.strip():
                                report.imports.append(sym.name)

                # Extract exports from symbol table
                symtab = elf.get_section_by_name(".symtab")
                if symtab:
                    for sym in symtab.iter_symbols():
                        if sym["st_info"]["type"] == "STT_FUNC" and sym.name:
                            # Only add non-empty function names
                            if sym.name.strip():
                                report.exports.append(sym.name)

        except OSError as e:
            logger.error(f"Error reading file: {e}")
            report.raw_backend_data["imports_exports_error"] = f"IO error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in ImportExportRecon: {e}")
            report.raw_backend_data["imports_exports_error"] = str(e)

        return report
