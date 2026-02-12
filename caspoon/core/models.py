from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class ProtectionInfo:
  pie: bool = False
  nx: bool = False
  canary: bool = False
  relro: str = "Unknown"
  
@dataclass
class FunctionInfo:
  name: str
  address: int
  imported: bool = False
  
@dataclass
class ExecutableReport:
  path: str
  arch: str = ""
  bits: int = 0
  file_type: str = ""
  stripped: bool = False
  protections: Optional[ProtectionInfo] = None
  strings: List[str] = field(default_factory=list)
  imports: List[str] = field(default_factory=list)
  exports: List[str] = field(default_factory=list)
  raw_backend_data: Dict = field(default_factory=dict)

  def pretty(self):
    return {
      "path": self.path,
      "arch": self.arch,
      "bits": self.bits,
      "file_type": self.file_type,
      "stripped": self.stripped,
      "protections": self.protections.__dict__ if self.protections else None,
      "imports": self.imports,
      "exports": self.exports,
      "strings_count": len(self.strings),
    }
