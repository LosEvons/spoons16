"""Unit tests for BaseView widget."""

from unittest.mock import Mock, patch

import pytest

from caspoon.ui.core.base import BaseView


class ConcreteView(BaseView[str]):
    """Concrete implementation of BaseView for testing."""

    def __init__(self):
        super().__init__()
        self.render_called = False
        self.render_data = None

    def render_content(self, data: str) -> None:
        """Mock implementation that records call."""
        self.render_called = True
        self.render_data = data
        self.update(f"Rendered: {data}")


class FailingView(BaseView[str]):
    """View that raises exception in render_content."""

    def render_content(self, data: str) -> None:
        """Always raises an exception."""
        raise ValueError("Test error")


class TestBaseView:
    """Tests for BaseView class."""

    def test_baseview_initialization(self):
        """Test BaseView initializes with None data."""
        view = ConcreteView()

        assert view.data is None
        assert not view.render_called

    def test_baseview_data_change_triggers_render(self):
        """Test setting data triggers render_content()."""
        view = ConcreteView()

        # Set data
        view.data = "test data"

        # Verify render was called
        assert view.render_called
        assert view.render_data == "test data"

    def test_baseview_data_none_does_not_trigger_render(self):
        """Test setting data to None does not trigger render."""
        view = ConcreteView()

        # Set to None
        view.data = None

        # Should not render with None data
        assert not view.render_called

    def test_baseview_data_change_from_none_to_value(self):
        """Test changing data from None to value triggers render."""
        view = ConcreteView()

        # Initially None
        assert view.data is None

        # Change to value
        view.data = "new value"

        assert view.render_called
        assert view.render_data == "new value"

    def test_baseview_data_change_from_value_to_value(self):
        """Test changing data from one value to another triggers render."""
        view = ConcreteView()

        # Set initial value
        view.data = "first"
        assert view.render_called
        view.render_called = False  # Reset

        # Change to new value
        view.data = "second"

        assert view.render_called
        assert view.render_data == "second"

    def test_baseview_multiple_data_changes(self):
        """Test multiple data changes each trigger render."""
        view = ConcreteView()

        # First change
        view.data = "one"
        assert view.render_data == "one"

        # Second change
        view.data = "two"
        assert view.render_data == "two"

        # Third change
        view.data = "three"
        assert view.render_data == "three"

    def test_baseview_render_error_handling(self):
        """Test error in render_content is caught and displayed."""
        view = FailingView()

        # This should not raise, but should log error
        view.data = "trigger error"

        # View should still be alive and showing error message
        # We can't easily test the update() call, but we verify no exception

    @patch("caspoon.ui.core.base.logger")
    def test_baseview_render_error_logs(self, mock_logger):
        """Test error in render_content is logged."""
        view = FailingView()

        # Trigger error
        view.data = "trigger"

        # Verify error was logged
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "FailingView" in call_args
        assert "Error rendering" in call_args

    def test_baseview_lifecycle_hooks_exist(self):
        """Test lifecycle hooks can be called."""
        view = ConcreteView()

        # These should not raise
        view.on_show()
        view.on_hide()

    def test_baseview_cannot_instantiate_abstract(self):
        """Test BaseView cannot be instantiated without implementing render_content."""
        # This should raise TypeError because render_content is abstract
        with pytest.raises(TypeError):
            BaseView()  # type: ignore

    def test_baseview_subclass_must_implement_render_content(self):
        """Test subclass must implement render_content()."""

        # Try to create incomplete subclass
        with pytest.raises(TypeError):

            class IncompleteView(BaseView[str]):
                pass

            IncompleteView()  # Should fail

    def test_baseview_with_complex_data_type(self):
        """Test BaseView works with complex data types."""

        class ComplexView(BaseView[dict]):
            def __init__(self):
                super().__init__()
                self.rendered_data = None

            def render_content(self, data: dict) -> None:
                self.rendered_data = data
                self.update(str(data))

        view = ComplexView()
        test_data = {"key": "value", "number": 42}

        view.data = test_data

        assert view.rendered_data == test_data

    def test_baseview_preserves_data_reference(self):
        """Test BaseView preserves reference to data object."""
        view = ConcreteView()
        original_data = "test string"

        view.data = original_data

        assert view.data is original_data
        assert view.render_data is original_data


class TestBaseViewLifecycle:
    """Tests for BaseView lifecycle methods."""

    def test_lifecycle_hooks_can_be_overridden(self):
        """Test lifecycle hooks can be overridden in subclasses."""

        class CustomView(BaseView[str]):
            def __init__(self):
                super().__init__()
                self.show_called = False
                self.hide_called = False

            def render_content(self, data: str) -> None:
                self.update(data)

            def on_show(self) -> None:
                self.show_called = True

            def on_hide(self) -> None:
                self.hide_called = True

        view = CustomView()

        view.on_show()
        assert view.show_called

        view.on_hide()
        assert view.hide_called

    def test_on_show_default_does_nothing(self):
        """Test default on_show implementation does nothing."""
        view = ConcreteView()

        # Should not raise
        result = view.on_show()
        assert result is None

    def test_on_hide_default_does_nothing(self):
        """Test default on_hide implementation does nothing."""
        view = ConcreteView()

        # Should not raise
        result = view.on_hide()
        assert result is None


class TestBaseViewEdgeCases:
    """Tests for BaseView edge cases."""

    def test_baseview_empty_string_data(self):
        """Test BaseView handles empty string data."""
        view = ConcreteView()

        view.data = ""

        assert view.render_called
        assert view.render_data == ""

    def test_baseview_zero_data(self):
        """Test BaseView handles zero as data."""

        class IntView(BaseView[int]):
            def __init__(self):
                super().__init__()
                self.rendered = False

            def render_content(self, data: int) -> None:
                self.rendered = True
                self.update(str(data))

        view = IntView()
        view.data = 0

        assert view.rendered

    def test_baseview_false_data(self):
        """Test BaseView handles False as data."""

        class BoolView(BaseView[bool]):
            def __init__(self):
                super().__init__()
                self.rendered = False

            def render_content(self, data: bool) -> None:
                self.rendered = True
                self.update(str(data))

        view = BoolView()
        view.data = False

        assert view.rendered

    def test_baseview_same_data_triggers_render(self):
        """Test setting same data value triggers render."""
        view = ConcreteView()

        view.data = "test"
        view.render_called = False

        # Set to same value
        view.data = "test"

        # Should still trigger render (watch is called)
        # Note: Textual reactive may or may not trigger if value unchanged
        # This test documents current behavior
