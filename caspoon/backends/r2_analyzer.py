"""Radare2 backend analyzer module."""

import json
import logging
from typing import Any

import r2pipe

logger = logging.getLogger(__name__)

# Configuration - Limits to prevent excessive memory usage and long parsing times
MAX_MAIN_INSTRUCTIONS = 200  # Limit instructions to analyze in main
MAX_XREF_FUNCTIONS = 100  # Limit number of functions to extract xrefs for
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
            - xrefs: Dict with 'to' and 'from' xrefs keyed by hex address

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

        # Extract cross-references for interactive navigation
        logger.debug("Extracting cross-references for functions")
        xrefs_to = {}  # xrefs to each address (who calls this)
        xrefs_from = {}  # xrefs from each address (what this calls)
        
        # Limit xref extraction to avoid performance issues
        funcs_for_xrefs = functions[:MAX_XREF_FUNCTIONS] if len(functions) > MAX_XREF_FUNCTIONS else functions
        
        for func in funcs_for_xrefs:
            addr = func.get("offset")
            if addr is None:
                continue
            
            # Convert address to hex format for consistency
            addr_hex = f"0x{addr:x}" if isinstance(addr, int) else str(addr)
            
            # Get xrefs TO this function (who calls it)
            try:
                xrefs_to_json = r2.cmd(f"axtj @ {addr}")
                xrefs_to_list = json.loads(xrefs_to_json) if xrefs_to_json.strip() else []
                if xrefs_to_list:
                    xrefs_to[addr_hex] = xrefs_to_list
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse xrefs-to JSON for {addr_hex}: {e}")
            except Exception as e:
                logger.warning(f"Error extracting xrefs-to for {addr_hex}: {e}")
            
            # Get xrefs FROM this function (what it calls)
            try:
                xrefs_from_json = r2.cmd(f"axfj @ {addr}")
                xrefs_from_list = json.loads(xrefs_from_json) if xrefs_from_json.strip() else []
                if xrefs_from_list:
                    xrefs_from[addr_hex] = xrefs_from_list
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse xrefs-from JSON for {addr_hex}: {e}")
            except Exception as e:
                logger.warning(f"Error extracting xrefs-from for {addr_hex}: {e}")

        logger.debug(
            f"Radare2 analysis complete: {len(functions)} functions, {len(imports)} imports, "
            f"{len(strings)} strings, {len(xrefs_to)} xrefs-to, {len(xrefs_from)} xrefs-from"
        )

        return {
            "functions": functions,
            "imports": imports,
            "strings": strings,
            "main_ops": main_ops,
            "xrefs": {
                "to": xrefs_to,
                "from": xrefs_from,
            },
        }

    finally:
        r2.quit()
