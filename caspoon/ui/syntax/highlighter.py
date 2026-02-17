"""Assembly instruction syntax highlighter."""

import re
from functools import lru_cache
from typing import Callable

from rich.text import Text

from .instructions import get_instruction_type
from .operand_parser import OperandParser, OperandType
from .schemes import ColorScheme, InstructionType, get_default_scheme


class AsmHighlighter:
    """Syntax highlighter for assembly code.

    Classifies instructions by type and applies color highlighting
    using Rich's Text API. Supports multiple architectures (x86/x64, ARM, MIPS).
    """

    def __init__(
        self,
        color_scheme: ColorScheme | None = None,
        enable_operand_parsing: bool = True,
        instruction_classifier: Callable[[str], InstructionType] | None = None,
        cache_size: int = 1000
    ):
        """Initialize the highlighter.

        Args:
            color_scheme: Optional color scheme. If None, uses the default scheme.
            enable_operand_parsing: If True, parse and highlight operands separately.
                                   If False, use legacy behavior (highlight entire instruction).
            instruction_classifier: Optional function to classify instructions by mnemonic.
                                   If None, uses the default x86/x64 classifier.
                                   Should be a function that takes a mnemonic string
                                   and returns an InstructionType.
            cache_size: Maximum number of cached highlighted instructions. Default is 1000.
        """
        self.scheme = color_scheme or get_default_scheme()
        self.enable_operand_parsing = enable_operand_parsing
        self.operand_parser = OperandParser() if enable_operand_parsing else None
        self.instruction_classifier = instruction_classifier or get_instruction_type
        
        # Cache configuration
        self._cache_enabled = True
        self._cache_size = cache_size
        
        # Create the cached method with specified cache size
        self._get_cached_markup = lru_cache(maxsize=cache_size)(self._get_cached_markup_impl)

        # Pattern to parse instruction lines
        # Handles formats like:
        #   mov rax, rbx
        #   mov rax, rbx ; comment
        #   push qword [rbp-0x10]
        self._instruction_pattern = re.compile(
            r'^\s*(?P<opcode>\S+)'  # Opcode (required)
            r'(?:\s+(?P<operands>[^;]+?))?'  # Operands (optional)
            r'(?:\s*;\s*(?P<comment>.*))?$',  # Comment (optional)
            re.IGNORECASE
        )

    def clear_cache(self) -> None:
        """Clear the highlight cache.
        
        Call this when switching binaries or when you want to free memory.
        """
        if hasattr(self, '_get_cached_markup'):
            self._get_cached_markup.cache_clear()

    def disable_cache(self) -> None:
        """Disable caching for testing or debugging.
        
        When disabled, instructions are highlighted fresh every time.
        """
        self._cache_enabled = False

    def enable_cache(self, size: int | None = None) -> None:
        """Enable caching with optional new size.
        
        Args:
            size: Optional new cache size. If None, uses current cache size.
        """
        self._cache_enabled = True
        if size is not None and size != self._cache_size:
            self._cache_size = size
            # Recreate the cached method with new size
            self._get_cached_markup = lru_cache(maxsize=size)(self._get_cached_markup_impl)
    
    def get_cache_info(self) -> dict[str, int]:
        """Get cache statistics.
        
        Returns:
            Dictionary with 'hits', 'misses', 'size', and 'maxsize' keys.
            Returns empty dict if cache is not available.
        """
        if not hasattr(self, '_get_cached_markup'):
            return {}
        
        info = self._get_cached_markup.cache_info()
        return {
            'hits': info.hits,
            'misses': info.misses,
            'size': info.currsize,
            'maxsize': info.maxsize or 0,
        }

    def classify_instruction(self, opcode: str) -> InstructionType:
        """Classify an instruction by its opcode.

        Args:
            opcode: The instruction opcode (may include operands).

        Returns:
            The instruction type classification.
        """
        if not opcode or not isinstance(opcode, str):
            return InstructionType.OTHER

        # Extract the base opcode (first token, lowercase)
        opcode_lower = opcode.strip().lower().split()[0] if opcode.strip() else ""

        if not opcode_lower:
            return InstructionType.OTHER

        # Use the provided instruction classifier
        return self.instruction_classifier(opcode_lower)

    def highlight_instruction(self, opcode: str, address: str = "") -> Text:
        """Create a highlighted Text object for an assembly instruction.
        
        Uses LRU cache for performance when cache is enabled.

        Args:
            opcode: The instruction opcode and operands.
            address: Optional address/offset to prepend.

        Returns:
            A Rich Text object with syntax highlighting applied.
        """
        if not self._cache_enabled:
            return self._highlight_instruction_impl(opcode, address)
        
        # Use cached version - convert markup string back to Text
        try:
            markup_str = self._get_cached_markup(opcode, address)
            return Text.from_markup(markup_str)
        except Exception:
            # If markup conversion fails, fall back to non-cached
            return self._highlight_instruction_impl(opcode, address)
    
    def _get_cached_markup_impl(self, opcode: str, address: str) -> str:
        """Cached implementation that returns markup string.
        
        This is wrapped by lru_cache in __init__. We return a markup string
        because Text objects are not hashable and cannot be cached directly.
        
        Args:
            opcode: The instruction opcode and operands.
            address: Optional address/offset to prepend.
            
        Returns:
            Rich markup string that can be converted back to Text.
        """
        text = self._highlight_instruction_impl(opcode, address)
        # Convert Text to markup string for caching
        return text.markup
    
    def _highlight_instruction_impl(self, opcode: str, address: str = "") -> Text:
        """Create a highlighted Text object for an assembly instruction.

        Args:
            opcode: The instruction opcode and operands.
            address: Optional address/offset to prepend.

        Returns:
            A Rich Text object with syntax highlighting applied.
        """
        try:
            # If operand parsing is disabled, use legacy behavior
            if not self.enable_operand_parsing:
                return self._highlight_instruction_legacy(opcode, address)

            # Parse the instruction line
            parsed = self._parse_instruction_line(opcode)

            if not parsed:
                # Failed to parse, fall back to legacy
                return self._highlight_instruction_legacy(opcode, address)

            # Build the highlighted text
            text = Text()

            # Add address if provided
            if address:
                text.append(f"{address}: ", style=self.scheme.address)

            # Add the opcode with appropriate color
            mnemonic = parsed['opcode']
            instr_type = self.classify_instruction(mnemonic)
            opcode_color = self.scheme.get_style(instr_type)
            text.append(mnemonic, style=opcode_color)

            # Add operands if present
            if parsed['operands']:
                text.append(" ")  # Space between opcode and operands
                self._highlight_operands(text, parsed['operands'])

            # Add comment if present
            if parsed['comment']:
                text.append(f"  ; {parsed['comment']}", style=self.scheme.comment)

            return text

        except Exception:
            # Graceful fallback: return plain text if highlighting fails
            text = Text()
            if address:
                text.append(f"{address}: ")
            text.append(opcode)
            return text

    def _highlight_instruction_legacy(self, opcode: str, address: str = "") -> Text:
        """Legacy highlighting: treat entire instruction as a single unit.

        This maintains backward compatibility with the original behavior.

        Args:
            opcode: The instruction opcode and operands.
            address: Optional address/offset to prepend.

        Returns:
            A Rich Text object with syntax highlighting applied.
        """
        # Classify the instruction
        instr_type = self.classify_instruction(opcode)

        # Get the appropriate color
        color = self.scheme.get_style(instr_type)

        # Build the highlighted text
        text = Text()

        # Add address if provided
        if address:
            text.append(f"{address}: ", style=self.scheme.address)

        # Add the instruction with appropriate color
        text.append(opcode, style=color)

        return text

    def _parse_instruction_line(self, line: str) -> dict[str, str] | None:
        """Parse an instruction line into components.

        Args:
            line: The instruction line to parse.

        Returns:
            Dictionary with 'opcode', 'operands', and 'comment' keys, or None if parsing fails.
        """
        match = self._instruction_pattern.match(line)

        if not match:
            return None

        return {
            'opcode': match.group('opcode') or "",
            'operands': (match.group('operands') or "").strip(),
            'comment': match.group('comment') or "",
        }

    def _highlight_operands(self, text: Text, operands_str: str) -> None:
        """Parse and highlight operands, appending to the given Text object.

        Args:
            text: The Text object to append to.
            operands_str: String containing comma-separated operands.
        """
        if not operands_str or not self.operand_parser:
            text.append(operands_str)
            return

        # Parse the operands
        operands = self.operand_parser.parse_operands(operands_str)

        for i, operand_info in enumerate(operands):
            # Add comma separator between operands
            if i > 0:
                text.append(", ", style=self.scheme.separator)

            # Get the appropriate color for this operand type
            color = self._get_operand_color(operand_info.operand_type)

            # Highlight the operand
            text.append(operand_info.value, style=color)

    def _get_operand_color(self, operand_type: OperandType) -> str:
        """Get the color for a given operand type.

        Args:
            operand_type: The type of operand.

        Returns:
            The Rich style string for this operand type.
        """
        if operand_type == OperandType.REGISTER:
            return self.scheme.register
        elif operand_type == OperandType.IMMEDIATE:
            return self.scheme.immediate
        elif operand_type == OperandType.MEMORY:
            return self.scheme.memory
        elif operand_type == OperandType.SYMBOL:
            return self.scheme.symbol
        else:
            return self.scheme.other
