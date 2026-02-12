
import json
from typing import Dict, Any

import r2pipe


def analyze_with_r2(path: str) -> Dict[str, Any]:
    """
    Lightweight radare2 analysis: functions, imports, strings, and main's disassembly.
    """
    r2 = r2pipe.open(path, flags=["-2"])
    try:
        # Basic analysis
        r2.cmd("aa")

        # Functions list
        funcs_json = r2.cmd("aflj")
        try:
            functions = json.loads(funcs_json) if funcs_json.strip() else []
        except json.JSONDecodeError:
            functions = []

        # Imported symbols
        imports_json = r2.cmd("isj")
        try:
            imports = json.loads(imports_json) if imports_json.strip() else []
        except json.JSONDecodeError:
            imports = []

        # Strings
        strings_json = r2.cmd("izj")
        try:
            strings = json.loads(strings_json) if strings_json.strip() else []
        except json.JSONDecodeError:
            strings = []

        # Disassembly of main (if it exists)
        r2.cmd("s main")
        main_ops_json = r2.cmd("pdj 200")  # first 200 instructions of main
        try:
            main_ops = json.loads(main_ops_json) if main_ops_json.strip() else []
        except json.JSONDecodeError:
            main_ops = []

        return {
            "functions": functions,
            "imports": imports,
            "strings": strings,
            "main_ops": main_ops,
        }

    finally:
        r2.quit()
