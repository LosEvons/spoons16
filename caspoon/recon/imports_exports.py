from elftools.elf.elffile import ELFFile

class ImportExportRecon:
  name = "imports_exports"

  def run(self, path: str, report):
    with open(path, "rb") as f:
      elf = ELFFile(f)

      # imports
      dynsym = elf.get_section_by_name(".dynsym")
      if dynsym:
        for sym in dynsym.iter_symbols():
          if sym['st_info']['type'] == 'STT_FUNC':
              report.imports.append(sym.name)

      # exports
      symtab = elf.get_section_by_name(".symtab")
      if symtab:
        for sym in symtab.iter_symbols():
          if sym['st_info']['type'] == 'STT_FUNC':
            report.exports.append(sym.name)

      return report
