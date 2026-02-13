"""Tests for InteractiveDisasmView widget."""

from unittest.mock import Mock, patch

import pytest

from caspoon.ui.navigation.manager import NavigationManager
from caspoon.ui.syntax import AsmHighlighter
from caspoon.ui.widgets.interactive_disasm import InteractiveDisasmView


class TestInteractiveDisasmViewInitialization:
    """Tests for InteractiveDisasmView initialization."""

    def test_widget_can_be_created(self):
        """Test that InteractiveDisasmView can be instantiated."""
        widget = InteractiveDisasmView()
        
        assert widget is not None
        assert isinstance(widget, InteractiveDisasmView)

    def test_widget_initializes_with_default_components(self):
        """Test that widget initializes with default navigation manager and highlighter."""
        widget = InteractiveDisasmView()
        
        assert widget.nav_manager is not None
        assert isinstance(widget.nav_manager, NavigationManager)
        assert widget.highlighter is not None
        assert isinstance(widget.highlighter, AsmHighlighter)

    def test_widget_accepts_custom_navigation_manager(self):
        """Test that widget can be initialized with a custom navigation manager."""
        custom_nav = NavigationManager()
        widget = InteractiveDisasmView(navigation_manager=custom_nav)
        
        assert widget.nav_manager is custom_nav

    def test_widget_accepts_custom_highlighter(self):
        """Test that widget can be initialized with a custom highlighter."""
        custom_highlighter = AsmHighlighter()
        widget = InteractiveDisasmView(highlighter=custom_highlighter)
        
        assert widget.highlighter is custom_highlighter

    def test_widget_initializes_with_empty_disasm_lines(self):
        """Test that widget starts with empty disassembly data."""
        widget = InteractiveDisasmView()
        
        assert widget.disasm_lines == []
        assert widget.current_function == ""

    def test_widget_starts_with_zero_selection(self):
        """Test that widget starts with first line selected."""
        widget = InteractiveDisasmView()
        
        assert widget.selected_line == 0

    def test_widget_can_take_focus(self):
        """Test that widget can receive keyboard focus."""
        widget = InteractiveDisasmView()
        
        assert widget.can_take_focus() is True


class TestDisassemblyDisplay:
    """Tests for disassembly display functionality."""

    def test_update_disassembly_with_valid_data(self):
        """Test updating widget with valid disassembly data."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": "push rbp"},
            {"offset": 0x401001, "opcode": "mov rbp, rsp"},
            {"offset": 0x401004, "opcode": "call 0x401100"},
        ]
        
        widget.update_disassembly(disasm_ops, "main")
        
        assert widget.disasm_lines == disasm_ops
        assert widget.current_function == "main"

    def test_update_disassembly_with_empty_data(self):
        """Test updating widget with empty disassembly data."""
        widget = InteractiveDisasmView()
        
        widget.update_disassembly([], "")
        
        assert widget.disasm_lines == []
        assert widget.current_function == ""

    def test_update_disassembly_selects_specified_address(self):
        """Test that update_disassembly selects line at specified address."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": "push rbp"},
            {"offset": 0x401001, "opcode": "mov rbp, rsp"},
            {"offset": 0x401004, "opcode": "call 0x401100"},
        ]
        
        widget.update_disassembly(disasm_ops, "main", current_address="0x401004")
        
        assert widget.selected_line == 2

    def test_render_disassembly_handles_no_data(self):
        """Test that render handles empty disassembly gracefully."""
        widget = InteractiveDisasmView()
        
        # Should not raise
        widget._render_disassembly()

    def test_render_line_formats_address_correctly(self):
        """Test that render_line formats addresses consistently."""
        widget = InteractiveDisasmView()
        
        op = {"offset": 0x401234, "opcode": "nop"}
        line = widget._render_line(op, False)
        
        # Check that address is in the line
        line_text = line.plain
        assert "0x00401234" in line_text

    def test_render_line_shows_selected_indicator(self):
        """Test that render_line shows selection indicator for selected lines."""
        widget = InteractiveDisasmView()
        
        op = {"offset": 0x401000, "opcode": "nop"}
        line = widget._render_line(op, True)
        
        line_text = line.plain
        assert widget.INDICATOR_SELECTED in line_text

    def test_render_line_shows_navigable_indicator(self):
        """Test that render_line shows navigation indicator for navigable instructions."""
        widget = InteractiveDisasmView()
        
        op = {"offset": 0x401000, "opcode": "call 0x401100"}
        line = widget._render_line(op, False)
        
        line_text = line.plain
        assert widget.INDICATOR_NAVIGABLE in line_text

    def test_render_line_no_navigable_indicator_for_normal_instructions(self):
        """Test that normal instructions don't show navigation indicator."""
        widget = InteractiveDisasmView()
        
        op = {"offset": 0x401000, "opcode": "mov rax, rbx"}
        line = widget._render_line(op, False)
        
        line_text = line.plain
        # Should not have the navigable indicator
        assert widget.INDICATOR_NAVIGABLE not in line_text or line_text.count(widget.INDICATOR_NAVIGABLE) == 0


class TestAddressExtraction:
    """Tests for address extraction from instructions."""

    def test_extract_hex_address(self):
        """Test extraction of hexadecimal addresses."""
        widget = InteractiveDisasmView()
        
        address = widget._extract_target_address("call 0x401234")
        
        assert address == "0x401234"

    def test_extract_symbol_address(self):
        """Test extraction of symbol addresses."""
        widget = InteractiveDisasmView()
        
        address = widget._extract_target_address("call sym.main")
        
        assert address == "sym.main"

    def test_extract_function_address(self):
        """Test extraction of function addresses."""
        widget = InteractiveDisasmView()
        
        address = widget._extract_target_address("jmp fcn.00401234")
        
        assert address == "fcn.00401234"

    def test_extract_address_from_jump(self):
        """Test extraction of addresses from jump instructions."""
        widget = InteractiveDisasmView()
        
        address = widget._extract_target_address("je 0x401100")
        
        assert address == "0x401100"

    def test_extract_address_returns_none_for_no_address(self):
        """Test that extraction returns None when no address is present."""
        widget = InteractiveDisasmView()
        
        address = widget._extract_target_address("mov rax, rbx")
        
        assert address is None

    def test_is_navigable_instruction_for_call(self):
        """Test that call instructions are identified as navigable."""
        widget = InteractiveDisasmView()
        
        assert widget._is_navigable_instruction("call 0x401234") is True

    def test_is_navigable_instruction_for_jump(self):
        """Test that jump instructions are identified as navigable."""
        widget = InteractiveDisasmView()
        
        assert widget._is_navigable_instruction("jmp 0x401234") is True
        assert widget._is_navigable_instruction("je 0x401234") is True
        assert widget._is_navigable_instruction("jne 0x401234") is True

    def test_is_navigable_instruction_for_normal_instructions(self):
        """Test that normal instructions are not identified as navigable."""
        widget = InteractiveDisasmView()
        
        assert widget._is_navigable_instruction("mov rax, rbx") is False
        assert widget._is_navigable_instruction("push rbp") is False
        assert widget._is_navigable_instruction("add rax, 5") is False

    def test_is_navigable_instruction_for_call_without_address(self):
        """Test that call without address is not navigable."""
        widget = InteractiveDisasmView()
        
        # Call to register (indirect call) shouldn't be navigable
        assert widget._is_navigable_instruction("call rax") is False

    def test_get_current_line_address(self):
        """Test getting the address of the current line."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": "push rbp"},
            {"offset": 0x401001, "opcode": "mov rbp, rsp"},
        ]
        widget.update_disassembly(disasm_ops)
        widget.selected_line = 1
        
        address = widget._get_current_line_address()
        
        assert address == "0x401001"

    def test_get_current_line_address_returns_none_for_invalid_selection(self):
        """Test that getting address returns None for invalid selection."""
        widget = InteractiveDisasmView()
        
        widget.selected_line = 999
        address = widget._get_current_line_address()
        
        assert address is None


class TestKeyboardNavigation:
    """Tests for keyboard navigation functionality."""

    def test_move_selection_down(self):
        """Test moving selection down."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": "push rbp"},
            {"offset": 0x401001, "opcode": "mov rbp, rsp"},
            {"offset": 0x401004, "opcode": "ret"},
        ]
        widget.update_disassembly(disasm_ops)
        widget.selected_line = 0
        
        widget._move_selection(1)
        
        assert widget.selected_line == 1

    def test_move_selection_up(self):
        """Test moving selection up."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": "push rbp"},
            {"offset": 0x401001, "opcode": "mov rbp, rsp"},
            {"offset": 0x401004, "opcode": "ret"},
        ]
        widget.update_disassembly(disasm_ops)
        widget.selected_line = 2
        
        widget._move_selection(-1)
        
        assert widget.selected_line == 1

    def test_move_selection_clamps_at_bottom(self):
        """Test that selection doesn't go past the last line."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": "push rbp"},
            {"offset": 0x401001, "opcode": "mov rbp, rsp"},
        ]
        widget.update_disassembly(disasm_ops)
        widget.selected_line = 1
        
        widget._move_selection(1)
        
        assert widget.selected_line == 1  # Should stay at last line

    def test_move_selection_clamps_at_top(self):
        """Test that selection doesn't go before the first line."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": "push rbp"},
            {"offset": 0x401001, "opcode": "mov rbp, rsp"},
        ]
        widget.update_disassembly(disasm_ops)
        widget.selected_line = 0
        
        widget._move_selection(-1)
        
        assert widget.selected_line == 0  # Should stay at first line

    def test_navigate_to_current_line_posts_message(self):
        """Test that navigating to current line posts a NavigateTo message."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": "call 0x401100"},
        ]
        widget.update_disassembly(disasm_ops)
        widget.selected_line = 0
        
        # Mock post_message to capture messages
        messages = []
        widget.post_message = lambda msg: messages.append(msg)
        
        widget._navigate_to_current_line()
        
        assert len(messages) == 1
        assert isinstance(messages[0], InteractiveDisasmView.NavigateTo)
        assert messages[0].address == "0x401100"

    def test_navigate_to_current_line_ignores_non_navigable(self):
        """Test that navigation ignores non-navigable instructions."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": "mov rax, rbx"},
        ]
        widget.update_disassembly(disasm_ops)
        widget.selected_line = 0
        
        messages = []
        widget.post_message = lambda msg: messages.append(msg)
        
        widget._navigate_to_current_line()
        
        # Should not post any messages for non-navigable instruction
        assert len(messages) == 0

    def test_jump_to_address_finds_and_selects_line(self):
        """Test that jump_to_address finds and selects the correct line."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": "push rbp"},
            {"offset": 0x401001, "opcode": "mov rbp, rsp"},
            {"offset": 0x401004, "opcode": "call 0x401100"},
        ]
        widget.update_disassembly(disasm_ops)
        widget.selected_line = 0
        
        messages = []
        widget.post_message = lambda msg: messages.append(msg)
        
        widget.jump_to_address("0x401004")
        
        assert widget.selected_line == 2
        assert len(messages) == 1


class TestNavigationHistory:
    """Tests for navigation history integration."""

    def test_go_back_calls_navigation_manager(self):
        """Test that go_back uses the navigation manager."""
        widget = InteractiveDisasmView()
        
        # Set up history
        widget.nav_manager.navigate_to("0x401000")
        widget.nav_manager.navigate_to("0x401100")
        
        messages = []
        widget.post_message = lambda msg: messages.append(msg)
        
        widget._go_back()
        
        assert len(messages) == 1
        assert isinstance(messages[0], InteractiveDisasmView.NavigateTo)
        assert messages[0].address == "0x401000"

    def test_go_forward_calls_navigation_manager(self):
        """Test that go_forward uses the navigation manager."""
        widget = InteractiveDisasmView()
        
        # Set up history
        widget.nav_manager.navigate_to("0x401000")
        widget.nav_manager.navigate_to("0x401100")
        widget.nav_manager.go_back()
        
        messages = []
        widget.post_message = lambda msg: messages.append(msg)
        
        widget._go_forward()
        
        assert len(messages) == 1
        assert isinstance(messages[0], InteractiveDisasmView.NavigateTo)
        assert messages[0].address == "0x401100"

    def test_navigate_adds_to_history(self):
        """Test that navigation adds current address to history."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": "call 0x401100"},
        ]
        widget.update_disassembly(disasm_ops)
        widget.selected_line = 0
        
        widget.post_message = lambda msg: None  # Ignore messages
        
        initial_history_len = len(widget.nav_manager.history)
        
        widget._navigate_to_current_line()
        
        # History should have one more entry
        assert len(widget.nav_manager.history) == initial_history_len + 1


class TestMessageEmission:
    """Tests for message emission."""

    def test_show_xrefs_posts_message(self):
        """Test that show_xrefs posts a ShowXrefs message."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": "call 0x401100"},
        ]
        widget.update_disassembly(disasm_ops)
        widget.selected_line = 0
        
        messages = []
        widget.post_message = lambda msg: messages.append(msg)
        
        widget._show_xrefs()
        
        assert len(messages) == 1
        assert isinstance(messages[0], InteractiveDisasmView.ShowXrefs)
        assert messages[0].address == "0x401000"

    def test_navigate_to_message_contains_address(self):
        """Test that NavigateTo message contains correct address."""
        msg = InteractiveDisasmView.NavigateTo("0x401234")
        
        assert msg.address == "0x401234"

    def test_show_xrefs_message_contains_address(self):
        """Test that ShowXrefs message contains correct address."""
        msg = InteractiveDisasmView.ShowXrefs("0x401234")
        
        assert msg.address == "0x401234"

    def test_open_goto_dialog_message_can_be_created(self):
        """Test that OpenGotoDialog message can be created."""
        msg = InteractiveDisasmView.OpenGotoDialog()
        
        assert msg is not None


class TestReactiveProperties:
    """Tests for reactive property behavior."""

    def test_selected_line_is_reactive(self):
        """Test that selected_line is a reactive property."""
        widget = InteractiveDisasmView()
        
        # Should be able to set and get
        widget.selected_line = 5
        assert widget.selected_line == 5

    def test_watch_selected_line_is_called(self):
        """Test that watch_selected_line method exists."""
        widget = InteractiveDisasmView()
        
        # Method should exist
        assert hasattr(widget, 'watch_selected_line')
        assert callable(widget.watch_selected_line)


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_opcode_handling(self):
        """Test handling of empty opcodes."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": ""},
        ]
        
        # Should not raise
        widget.update_disassembly(disasm_ops)
        widget._render_disassembly()

    def test_missing_opcode_handling(self):
        """Test handling of missing opcode field."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000},
        ]
        
        # Should not raise
        widget.update_disassembly(disasm_ops)
        widget._render_disassembly()

    def test_missing_offset_handling(self):
        """Test handling of missing offset field."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"opcode": "nop"},
        ]
        
        # Should not raise
        widget.update_disassembly(disasm_ops)
        widget._render_disassembly()

    def test_malformed_address_in_instruction(self):
        """Test handling of malformed addresses in instructions."""
        widget = InteractiveDisasmView()
        
        address = widget._extract_target_address("call invalid")
        
        assert address is None

    def test_navigate_with_invalid_selection(self):
        """Test navigation with invalid selection index."""
        widget = InteractiveDisasmView()
        
        widget.selected_line = 999
        
        # Should not raise
        widget._navigate_to_current_line()

    def test_show_xrefs_with_invalid_selection(self):
        """Test show_xrefs with invalid selection."""
        widget = InteractiveDisasmView()
        
        widget.selected_line = 999
        
        messages = []
        widget.post_message = lambda msg: messages.append(msg)
        
        widget._show_xrefs()
        
        # Should not post message for invalid selection
        assert len(messages) == 0


class TestARMInstructions:
    """Tests for ARM instruction support."""

    def test_arm_branch_is_navigable(self):
        """Test that ARM branch instructions are identified as navigable."""
        widget = InteractiveDisasmView()
        
        assert widget._is_navigable_instruction("b 0x1234") is True
        assert widget._is_navigable_instruction("bl 0x1234") is True
        assert widget._is_navigable_instruction("beq 0x1234") is True

    def test_arm_branch_address_extraction(self):
        """Test extraction of addresses from ARM branches."""
        widget = InteractiveDisasmView()
        
        address = widget._extract_target_address("bl 0x401234")
        
        assert address == "0x401234"


class TestIntegration:
    """Integration tests for the widget."""

    def test_complete_navigation_flow(self):
        """Test a complete navigation flow with history."""
        widget = InteractiveDisasmView()
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": "push rbp"},
            {"offset": 0x401001, "opcode": "call 0x401100"},
            {"offset": 0x401006, "opcode": "ret"},
        ]
        widget.update_disassembly(disasm_ops, "main")
        
        messages = []
        widget.post_message = lambda msg: messages.append(msg)
        
        # Select the call instruction
        widget.selected_line = 1
        
        # Navigate to it
        widget._navigate_to_current_line()
        
        # Should post NavigateTo message
        assert len(messages) == 1
        assert messages[0].address == "0x401100"
        
        # Should be in history
        assert len(widget.nav_manager.history) == 1

    def test_widget_with_custom_components(self):
        """Test widget with custom navigation manager and highlighter."""
        nav_manager = NavigationManager()
        highlighter = AsmHighlighter()
        
        widget = InteractiveDisasmView(
            navigation_manager=nav_manager,
            highlighter=highlighter
        )
        
        disasm_ops = [
            {"offset": 0x401000, "opcode": "nop"},
        ]
        widget.update_disassembly(disasm_ops)
        
        # Should use the custom components
        assert widget.nav_manager is nav_manager
        assert widget.highlighter is highlighter
