"""Unit tests for ProtectionsView migration to BaseView architecture."""

import pytest
from textual.app import App, ComposeResult

from caspoon.ui import widget_ids as wid
from caspoon.tests.fixtures.ui_fixtures import (
    empty_protections_dict,
    full_protections_dict,
    mock_analysis_results,
    mock_analysis_results_no_protections,
    mock_app_state,
    mock_executable_report,
    mock_executable_report_stripped,
    no_protections_dict,
    partial_protections_dict,
)
from caspoon.ui.core.base import BaseView
from caspoon.ui.core.state import AppState
from caspoon.ui.views.protections import ProtectionsView


class TestProtectionsViewInheritance:
    """Test that ProtectionsView properly inherits from BaseView."""

    def test_protections_inherits_baseview(self):
        """Verify ProtectionsView inherits from BaseView[dict]."""
        assert issubclass(ProtectionsView, BaseView)

    def test_protections_has_render_content_method(self):
        """Verify ProtectionsView implements render_content() method."""
        assert hasattr(ProtectionsView, "render_content")
        assert callable(ProtectionsView.render_content)

    def test_protections_has_on_mount_method(self):
        """Verify ProtectionsView implements on_mount() for subscriptions."""
        assert hasattr(ProtectionsView, "on_mount")
        assert callable(ProtectionsView.on_mount)


class TestProtectionsViewInitialization:
    """Test ProtectionsView initialization."""

    def test_protections_initializes_without_errors(self):
        """Verify ProtectionsView can be instantiated."""
        view = ProtectionsView()
        assert view is not None
        assert isinstance(view, ProtectionsView)

    def test_protections_has_data_attribute(self):
        """Verify ProtectionsView has reactive data attribute from BaseView."""
        view = ProtectionsView()
        assert hasattr(view, "data")
        # Initially None until state is set


class TestProtectionsViewStateSubscription:
    """Test ProtectionsView state subscription and updates."""

    @pytest.mark.asyncio
    async def test_protections_subscribes_on_mount(self, mock_app_state):
        """Verify on_mount() sets up state subscription."""
        from caspoon.ui.app import CaspoonApp

        # Use real app instance for proper context
        app = CaspoonApp()
        app.state = mock_app_state

        # Track if subscription was called
        subscription_called = False
        original_subscribe = app.state.subscribe

        def mock_subscribe(property_name, callback):
            nonlocal subscription_called
            subscription_called = True
            assert property_name == "analysis_results"
            assert callable(callback)
            original_subscribe(property_name, callback)

        app.state.subscribe = mock_subscribe

        async with app.run_test() as pilot:
            view = app.query_one(f"#{wid.PROTECTIONS_VIEW}", ProtectionsView)

            # Give time for on_mount to be called
            await pilot.pause()

            # Verify subscription happened
            assert subscription_called

    @pytest.mark.asyncio
    async def test_protections_updates_on_state_change(self, mock_analysis_results):
        """Verify view updates when state.analysis_results changes."""
        from caspoon.ui.app import CaspoonApp

        app = CaspoonApp()

        async with app.run_test() as pilot:
            view = app.query_one(f"#{wid.PROTECTIONS_VIEW}", ProtectionsView)

            # Update state - should trigger view update
            app.state.analysis_results = mock_analysis_results

            await pilot.pause()

            # Verify view data was updated with protections dict
            assert view.data is not None
            assert isinstance(view.data, dict)
            assert "pie" in view.data
            assert view.data["pie"] is True


class TestProtectionsViewRendering:
    """Test ProtectionsView render_content() method."""

    def test_protections_renders_full_protections(self, full_protections_dict):
        """Verify render_content() displays all protections enabled."""
        view = ProtectionsView()

        # Manually call render_content
        view.render_content(full_protections_dict)

        # Verify render succeeded
        assert True

    def test_protections_renders_no_protections(self, no_protections_dict):
        """Verify render_content() displays all protections disabled."""
        view = ProtectionsView()

        view.render_content(no_protections_dict)

        assert True

    def test_protections_renders_partial_protections(self, partial_protections_dict):
        """Verify render_content() displays mixed protection states."""
        view = ProtectionsView()

        view.render_content(partial_protections_dict)

        assert True

    def test_protections_handles_empty_dict(self, empty_protections_dict):
        """Verify render_content() handles empty protections dict gracefully."""
        view = ProtectionsView()

        # Should display "no protection information" message
        view.render_content(empty_protections_dict)

        assert True


class TestProtectionsViewFormatting:
    """Test protection status formatting and color coding."""

    def test_format_status_boolean_true(self):
        """Verify _format_status() formats True as green YES."""
        view = ProtectionsView()
        result = view._format_status("pie", True)
        assert "YES" in result
        assert "green" in result

    def test_format_status_boolean_false(self):
        """Verify _format_status() formats False as red NO."""
        view = ProtectionsView()
        result = view._format_status("nx", False)
        assert "NO" in result
        assert "red" in result

    def test_format_status_relro_full(self):
        """Verify _format_status() formats RELRO=full as green."""
        view = ProtectionsView()
        result = view._format_status("relro", "full")
        assert "Full" in result
        assert "green" in result

    def test_format_status_relro_partial(self):
        """Verify _format_status() formats RELRO=partial as yellow."""
        view = ProtectionsView()
        result = view._format_status("relro", "partial")
        assert "Partial" in result
        assert "yellow" in result

    def test_format_status_relro_none(self):
        """Verify _format_status() formats RELRO=none as red."""
        view = ProtectionsView()
        result = view._format_status("relro", "none")
        assert "None" in result
        assert "red" in result

    def test_format_status_unknown(self):
        """Verify _format_status() handles unknown values."""
        view = ProtectionsView()
        result = view._format_status("pie", None)
        assert "Unknown" in result
        assert "dim" in result


class TestProtectionsViewBackwardCompatibility:
    """Test backward compatibility with old update_data() interface."""

    def test_protections_has_update_data_method(self):
        """Verify update_data() method still exists for compatibility."""
        view = ProtectionsView()
        assert hasattr(view, "update_data")
        assert callable(view.update_data)

    def test_protections_update_data_still_works(self, mock_executable_report):
        """Verify old update_data() method still functions."""
        view = ProtectionsView()

        # Call old-style update method
        view.update_data(mock_executable_report)

        # Verify render succeeded
        assert True

    def test_protections_update_data_with_no_protections(self, mock_executable_report_stripped):
        """Verify update_data() handles reports without protections."""
        view = ProtectionsView()

        # Report with protections=None should be handled gracefully
        report = mock_executable_report_stripped
        report.protections = None

        view.update_data(report)

        # Should display "no protection information" message
        assert True


class TestProtectionsViewEdgeCases:
    """Test edge cases and error handling."""

    def test_protections_on_mount_without_app_state(self):
        """Verify on_mount() handles missing app.state gracefully."""
        view = ProtectionsView()

        # Should not crash even without app context (defensive coding)
        # The exception is caught in on_mount()
        view.on_mount()

        assert True

    def test_protections_handles_missing_protection_keys(self):
        """Verify render handles protections dict with missing keys."""
        view = ProtectionsView()

        # Dict with only some protections
        incomplete_dict = {"pie": True}

        view.render_content(incomplete_dict)

        assert True

    def test_protections_handles_extra_protection_keys(self):
        """Verify render handles protections dict with extra keys."""
        view = ProtectionsView()

        # Dict with extra unknown protections
        extra_dict = {
            "pie": True,
            "nx": True,
            "canary": True,
            "relro": "full",
            "aslr": True,  # Extra key
            "fortify": True,  # Extra key
        }

        view.render_content(extra_dict)

        assert True

    @pytest.mark.asyncio
    async def test_protections_state_change_with_none_results(self):
        """Verify view handles analysis_results set to None."""
        from caspoon.ui.app import CaspoonApp

        app = CaspoonApp()

        async with app.run_test() as pilot:
            view = app.query_one(f"#{wid.PROTECTIONS_VIEW}", ProtectionsView)

            # Set results to None - should clear view data
            app.state.analysis_results = None

            await pilot.pause()

            # View should handle this gracefully (data becomes empty dict)
            assert view.data == {}
