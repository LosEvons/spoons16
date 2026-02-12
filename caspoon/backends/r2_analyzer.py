"""Radare2 backend analyzer module."""

import json
import logging
from typing import Dict, Any

import r2pipe

logger = logging.getLogger(__name__)

# Configuration
MAX_MAIN_INSTRUCTIONS = 200  # Limit instructions to analyze in main
ANALYSIS_TIMEOUT = 60  # Timeout for r2 commands in seconds


def analyze_with_r2(path: str) -> Dict[str, Any]:
    """Perform lightweight radare2 analysis on an executable.
    
    Analyzes functions, imports, strings, and disassembles the main function.
    
    Args:
        path: Path to the executable file
        
    Returns:
        Dictionary containing analysis results with keys:
            - functions: List of functions found
            - imports: List of imported symbols
            - strings: List of strings found
            - main_ops: Disassembly of main function
            
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

        logger.debug(f"Radare2 analysis complete: {len(functions)} functions, {len(imports)} imports, {len(strings)} strings")
        
        return {
            "functions": functions,
            "imports": imports,
            "strings": strings,
            "main_ops": main_ops,
        }

    finally:
        r2.quit()
