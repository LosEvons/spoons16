"""Radare2 backend analyzer module."""

import json
import logging
from typing import Any

import r2pipe

logger = logging.getLogger(__name__)

# Configuration - Limits to prevent excessive memory usage and long parsing times
MAX_MAIN_INSTRUCTIONS = 200  # Limit instructions to analyze in main
ANALYSIS_TIMEOUT = 60  # Timeout for r2 commands in seconds


def analyze_with_r2(path: str) -> dict[str, Any]:
    """Perform lightweight radare2 analysis on an executable.

    Analyzes functions, imports, strings, disassembles the main function,
    and extracts cross-references for interactive navigation.

    Args:
        path: Path to the executable file

    Returns:
        Dictionary containing analysis results with keys:
            - functions: List of functions found
            - imports: List of imported symbols
            - strings: List of strings found
            - main_ops: Disassembly of main function
            - xrefs: Dictionary of cross-references by address

    Raises:
        Exception: If r2pipe fails to open the file or analysis fails
    """
    logger.debug(f"Starting radare2 analysis on {path}")

    r2 = r2pipe.open(path, flags=["-2"])
    try:
        # Basic analysis (lightweight)
        r2.cmd("aa")

        # Functions list
        funcs_json = r2.cmd("aflj")
        try:
            functions = json.loads(funcs_json) if funcs_json.strip() else []
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse functions JSON: {e}")
            functions = []

        # Imported symbols
        imports_json = r2.cmd("isj")
        try:
            imports = json.loads(imports_json) if imports_json.strip() else []
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse imports JSON: {e}")
            imports = []

        # Strings
        strings_json = r2.cmd("izj")
        try:
            strings = json.loads(strings_json) if strings_json.strip() else []
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse strings JSON: {e}")
            strings = []

        # Disassembly of main (if it exists)
        r2.cmd("s main")
        main_ops_json = r2.cmd(f"pdj {MAX_MAIN_INSTRUCTIONS}")
        try:
            main_ops = json.loads(main_ops_json) if main_ops_json.strip() else []
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse main disassembly JSON: {e}")
            main_ops = []

        # Extract cross-references for analyzed functions
        xrefs = _extract_xrefs(r2, functions)

        logger.debug(
            f"Radare2 analysis complete: {len(functions)} functions, "
            f"{len(imports)} imports, {len(strings)} strings, "
            f"{len(xrefs)} functions with xrefs"
        )

        return {
            "functions": functions,
            "imports": imports,
            "strings": strings,
            "main_ops": main_ops,
            "xrefs": xrefs,
        }

    finally:
        r2.quit()


def _extract_xrefs(r2: Any, functions: list[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Extract cross-references for analyzed functions.

    For each function, extracts:
    - callers (xrefs TO this function) using axtj
    - callees (xrefs FROM this function) using axfj

    Args:
        r2: r2pipe instance
        functions: List of function dictionaries with 'offset' field

    Returns:
        Dictionary mapping hex address strings to xref data:
        {
            "0x401000": {
                "callers": [{"from": 4198400, "type": "CALL", "fcn_name": "main"}, ...],
                "callees": [{"to": 4198656, "type": "CALL", "fcn_name": "sub_401020"}, ...]
            }
        }
    """
    xrefs_dict = {}

    for func in functions:
        try:
            # Get function address (offset)
            func_addr = func.get("offset")
            if func_addr is None:
                continue

            # Convert to hex string for consistent key format
            hex_addr = f"0x{func_addr:x}"

            # Extract xrefs TO this function (callers)
            callers_json = r2.cmd(f"axtj @ {func_addr}")
            try:
                callers = json.loads(callers_json) if callers_json.strip() else []
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse callers JSON for {hex_addr}: {e}")
                callers = []

            # Extract xrefs FROM this function (callees)
            callees_json = r2.cmd(f"axfj @ {func_addr}")
            try:
                callees = json.loads(callees_json) if callees_json.strip() else []
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse callees JSON for {hex_addr}: {e}")
                callees = []

            # Only add to dict if we have at least some xrefs
            if callers or callees:
                xrefs_dict[hex_addr] = {
                    "callers": callers,
                    "callees": callees,
                }

        except Exception as e:
            # Don't fail entire analysis if xref extraction fails for one function
            logger.warning(f"Failed to extract xrefs for function: {e}")
            continue

    return xrefs_dict
