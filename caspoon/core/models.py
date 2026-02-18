"""Data models for executable analysis reports."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProtectionInfo:
    """Security protection information for an executable.

    Attributes:
        pie: Position Independent Executable enabled
        nx: No-Execute bit enabled
        canary: Stack canary protection enabled
        relro: RELRO protection level (full/partial/none/Unknown)
    """

    pie: bool = False
    nx: bool = False
    canary: bool = False
    relro: str = "Unknown"


@dataclass
class FunctionInfo:
    """Function metadata.

    Attributes:
        name: Function name
        address: Function address in memory
        imported: Whether this is an imported function
    """

    name: str
    address: int
    imported: bool = False


@dataclass
class ExecutableReport:
    """Main report object containing all analysis results.

    Attributes:
        path: Path to the analyzed executable
        arch: Architecture (e.g., x86_64, ARM)
        bits: Bit width (32 or 64), or None if unknown
        file_type: File type description
        stripped: Whether debug symbols are stripped
        protections: Security protection information
        strings: List of extracted strings
        imports: List of imported functions
        exports: List of exported functions
        raw_backend_data: Backend-specific data (e.g., radare2 JSON)
    """

    path: str
    arch: str = ""
    bits: int | None = None
    file_type: str = ""
    stripped: bool = False
    protections: ProtectionInfo | None = None
    strings: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    raw_backend_data: dict[str, Any] = field(default_factory=dict)

    def pretty(self) -> dict[str, Any]:
        """Return a pretty dictionary representation of the report.

        Returns:
            Dictionary with formatted report data
        """
        return {
            "path": self.path,
            "arch": self.arch,
            "bits": self.bits if self.bits is not None else "unknown",
            "file_type": self.file_type,
            "stripped": self.stripped,
            "protections": self.protections.__dict__ if self.protections else None,
            "imports": self.imports,
            "exports": self.exports,
            "strings_count": len(self.strings),
        }
