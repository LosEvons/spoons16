# Subtask 5: Async Analysis Workers

## Objective

Implement async worker pattern for non-blocking binary analysis, allowing the TUI to remain responsive during long-running analysis operations with progress reporting and cancellation support.

## Scope

**Included:**
- Base Worker class for async operations with lifecycle management
- AnalysisWorker for binary analysis using ReconRunner
- Progress reporting system via messages and AppState
- Cancellation support (user can cancel analysis mid-flight)
- Integration with ReconRunner (run in background thread)
- Worker state management (idle, running, completed, failed, cancelled)
- Unit tests for worker logic without actual analysis
- Integration tests with mocked ReconRunner

**Excluded:**
- Multi-panel layout (covered in Subtask 7)
- Command palette (covered in Subtask 6)
- Additional worker types beyond analysis (future enhancement)
- Distributed/parallel analysis (future enhancement)

## Technical Approach

### 1. Base Worker Class
**Location**: `caspoon/ui/workers/base.py`

Foundation for all async operations:

- **Worker States**: idle, running, completed, failed, cancelled
- **Lifecycle Methods**:
  - `async def run()` - Main work method (abstract)
  - `async def cancel()` - Graceful cancellation
  - `on_complete()` - Success callback
  - `on_error(error)` - Error callback
- **Progress Reporting**:
  - `report_progress(percent, message)` - Update UI
  - Posts ProgressUpdate message
- **Error Handling**: Catch and report exceptions
- **State Transitions**: idle → running → completed/failed/cancelled

### 2. AnalysisWorker
**Location**: `caspoon/ui/workers/analysis.py`

Specific worker for binary analysis:

- **Input**: Binary file path
- **Output**: ExecutableReport
- **Process**:
  1. Validate file exists
  2. Initialize ReconRunner
  3. Run analysis in background thread (asyncio.to_thread)
  4. Report progress at key stages (loading, analyzing, extracting)
  5. Update AppState on completion
  6. Handle cancellation (interrupt ReconRunner if possible)
- **Progress Stages**:
  - 10%: File loaded
  - 30%: Binary info extracted
  - 50%: Functions analyzed
  - 70%: Strings extracted
  - 90%: Finalizing
  - 100%: Complete
- **Error Handling**: File not found, invalid format, r2 unavailable

### 3. Integration with CaspoonApp
**Location**: `caspoon/ui/app.py`

Wire up async workers to the app:

- **Worker Storage**: `self._current_worker: Optional[Worker] = None`
- **Action Methods**:
  - `async def start_analysis(path: str)` - Create and start AnalysisWorker
  - `async def cancel_analysis()` - Cancel current worker
- **Message Handlers**:
  - Handle StartAnalysis message → start_analysis()
  - Handle CancelAnalysis message → cancel_analysis()
  - Handle ProgressUpdate message → update UI
- **State Management**:
  - Update `app.state.ui_state.is_analyzing`
  - Update `app.state.ui_state.analysis_progress`
  - Update `app.state.ui_state.analysis_message`
- **Completion Handling**:
  - On success: `app.state.update_from_report(report)`
  - On error: show error message
  - On cancel: reset state

### 4. Progress UI
**Location**: View components and status bar

Display progress to user:

- **Status Bar**: Show "Analyzing... 45%" with message
- **Progress Bar** (optional): Visual progress indicator
- **Cancel Button**: Ctrl+C or ESC to cancel
- **Spinner Animation**: Show activity during indeterminate stages

### 5. Cancellation Logic

Graceful cancellation support:

- **User Trigger**: Ctrl+C or ESC key
- **Worker Check**: Worker checks `self._cancelled` flag periodically
- **Cleanup**: Close ReconRunner, release resources
- **State Reset**: Clear is_analyzing flag, reset progress
- **Message**: Post AnalysisCancelled message

## Implementation Steps

### Step 1: Implement Base Worker (2.5 hours)
Create `caspoon/ui/workers/base.py`:
- Import asyncio, enum for states, logging
- Define WorkerState enum: IDLE, RUNNING, COMPLETED, FAILED, CANCELLED
- Create Worker base class:
  ```python
  from abc import ABC, abstractmethod
  from enum import Enum
  import asyncio
  import logging
  
  class WorkerState(Enum):
      IDLE = "idle"
      RUNNING = "running"
      COMPLETED = "completed"
      FAILED = "failed"
      CANCELLED = "cancelled"
  
  class Worker(ABC):
      def __init__(self, app):
          self.app = app
          self.state = WorkerState.IDLE
          self._cancelled = False
          self._task = None
          self.logger = logging.getLogger(self.__class__.__name__)
      
      @abstractmethod
      async def run(self):
          """Execute the work. Must be implemented by subclass."""
          pass
      
      async def start(self):
          """Start the worker."""
          self.state = WorkerState.RUNNING
          self._task = asyncio.create_task(self._run_with_error_handling())
      
      async def _run_with_error_handling(self):
          """Run with error handling wrapper."""
          try:
              result = await self.run()
              if not self._cancelled:
                  self.state = WorkerState.COMPLETED
                  self.on_complete(result)
          except Exception as e:
              self.logger.error(f"Worker error: {e}")
              self.state = WorkerState.FAILED
              self.on_error(e)
      
      async def cancel(self):
          """Cancel the worker."""
          self._cancelled = True
          if self._task:
              self._task.cancel()
          self.state = WorkerState.CANCELLED
          self.on_cancel()
      
      def report_progress(self, percent: int, message: str):
          """Report progress to app."""
          from caspoon.ui.core.messages import ProgressUpdate
          self.app.post_message(ProgressUpdate(percent, message))
      
      def on_complete(self, result):
          """Called on successful completion. Override to handle result."""
          pass
      
      def on_error(self, error):
          """Called on error. Override to handle error."""
          pass
      
      def on_cancel(self):
          """Called on cancellation. Override for cleanup."""
          pass
  ```

### Step 2: Implement AnalysisWorker (3 hours)
Create `caspoon/ui/workers/analysis.py`:
- Import Worker base class, asyncio, ReconRunner
- Create AnalysisWorker(Worker):
  ```python
  from pathlib import Path
  import asyncio
  from caspoon.ui.workers.base import Worker
  from caspoon.recon import ReconRunner
  
  class AnalysisWorker(Worker):
      def __init__(self, app, file_path: str):
          super().__init__(app)
          self.file_path = file_path
          self.runner = None
      
      async def run(self):
          """Run binary analysis."""
          # Validate file
          if not Path(self.file_path).exists():
              raise FileNotFoundError(f"File not found: {self.file_path}")
          
          self.report_progress(10, "Loading binary...")
          
          # Initialize ReconRunner (blocking operation)
          await asyncio.sleep(0.1)  # Yield to event loop
          self.runner = ReconRunner(self.file_path)
          
          self.report_progress(30, "Extracting binary info...")
          
          # Run analysis in thread (blocking operation)
          report = await asyncio.to_thread(self._run_analysis)
          
          self.report_progress(100, "Analysis complete")
          return report
      
      def _run_analysis(self):
          """Run analysis (blocking). Called in thread."""
          # This runs in a background thread
          if self._cancelled:
              return None
          
          self.runner.analyze()
          
          # Simulate progress reporting for long operations
          # In reality, ReconRunner would need to support callbacks
          
          return self.runner.get_report()
      
      def on_complete(self, result):
          """Update app state with results."""
          if result:
              self.app.state.update_from_report(result)
              from caspoon.ui.core.messages import AnalysisComplete
              self.app.post_message(AnalysisComplete(result))
      
      def on_error(self, error):
          """Post error message."""
          from caspoon.ui.core.messages import AnalysisError
          self.app.post_message(AnalysisError(str(error)))
      
      def on_cancel(self):
          """Cleanup on cancellation."""
          if self.runner:
              # Close runner if possible
              pass
          from caspoon.ui.core.messages import AnalysisCancelled
          self.app.post_message(AnalysisCancelled())
  ```

### Step 3: Add New Messages (30 minutes)
Update `caspoon/ui/core/messages.py`:
- Add ProgressUpdate message:
  ```python
  class ProgressUpdate(Message):
      def __init__(self, percent: int, message: str):
          self.percent = percent
          self.message = message
          super().__init__()
  ```
- Add AnalysisCancelled message:
  ```python
  class AnalysisCancelled(Message):
      """Analysis was cancelled by user."""
      pass
  ```
- Update existing AnalysisComplete, AnalysisError if needed

### Step 4: Integrate with CaspoonApp (3 hours)
Modify `caspoon/ui/app.py`:
- Add worker instance variable: `self._current_worker: Optional[Worker] = None`
- Replace synchronous analysis with async worker:
  ```python
  async def start_analysis(self, path: str) -> None:
      """Start binary analysis in background worker."""
      # Cancel any existing analysis
      if self._current_worker:
          await self._current_worker.cancel()
      
      # Create and start new worker
      from caspoon.ui.workers.analysis import AnalysisWorker
      self._current_worker = AnalysisWorker(self, path)
      
      # Update UI state
      self.state.ui_state.is_analyzing = True
      self.state.ui_state.analysis_progress = 0
      self.state.ui_state.analysis_message = "Starting analysis..."
      
      # Start worker
      await self._current_worker.start()
  
  async def cancel_analysis(self) -> None:
      """Cancel current analysis."""
      if self._current_worker:
          await self._current_worker.cancel()
          self._current_worker = None
          self.state.ui_state.is_analyzing = False
          self.state.ui_state.analysis_progress = 0
          self.notify("Analysis cancelled")
  ```
- Add message handlers:
  ```python
  def on_start_analysis(self, message: StartAnalysis) -> None:
      """Handle start analysis message."""
      asyncio.create_task(self.start_analysis(message.path))
  
  def on_progress_update(self, message: ProgressUpdate) -> None:
      """Handle progress update."""
      self.state.ui_state.analysis_progress = message.percent
      self.state.ui_state.analysis_message = message.message
  
  def on_analysis_complete(self, message: AnalysisComplete) -> None:
      """Handle analysis completion."""
      self.state.ui_state.is_analyzing = False
      self.state.ui_state.analysis_progress = 100
      self.notify("Analysis complete", severity="success")
      self._current_worker = None
  
  def on_analysis_error(self, message: AnalysisError) -> None:
      """Handle analysis error."""
      self.state.ui_state.is_analyzing = False
      self.notify(f"Analysis failed: {message.error}", severity="error")
      self._current_worker = None
  
  def on_analysis_cancelled(self, message: AnalysisCancelled) -> None:
      """Handle analysis cancellation."""
      self.state.ui_state.is_analyzing = False
      self.notify("Analysis cancelled", severity="warning")
  ```
- Add keybinding for cancellation: Ctrl+C or ESC when analyzing

### Step 5: Update Status Bar (1.5 hours)
Modify status bar or footer to show progress:
- Add progress indicator widget to footer
- Watch `app.state.ui_state.is_analyzing`
- Watch `app.state.ui_state.analysis_progress`
- Watch `app.state.ui_state.analysis_message`
- Display: "[Analyzing... 45%] Extracting strings..." when analyzing
- Display: "Ready" when idle
- Add spinner animation (rotating chars: ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏)
- Show cancel hint: "Press Ctrl+C to cancel"

### Step 6: Unit Tests for Base Worker (2 hours)
Create `caspoon/tests/unit/ui/workers/test_base.py`:
- `test_worker_initial_state()` - Verify starts in IDLE
- `test_worker_state_transitions()` - Verify state changes
- `test_worker_start()` - Can start worker
- `test_worker_run_must_be_implemented()` - Abstract method enforced
- `test_worker_cancel()` - Cancel sets flag and state
- `test_worker_progress_reporting()` - report_progress posts message
- `test_worker_on_complete_called()` - Success callback invoked
- `test_worker_on_error_called()` - Error callback invoked
- `test_worker_on_cancel_called()` - Cancel callback invoked
- `test_worker_error_handling()` - Exceptions caught and handled
- Create mock worker subclass for testing
- Use asyncio test utilities (pytest-asyncio)
- Aim for >90% coverage

### Step 7: Unit Tests for AnalysisWorker (2 hours)
Create `caspoon/tests/unit/ui/workers/test_analysis.py`:
- `test_analysis_worker_initialization()` - Can create with file path
- `test_analysis_worker_file_not_found()` - Raises error for missing file
- `test_analysis_worker_run_analysis()` - Mock ReconRunner, verify flow
- `test_analysis_worker_progress_stages()` - Verify progress messages
- `test_analysis_worker_on_complete_updates_state()` - State updated
- `test_analysis_worker_on_error_posts_message()` - Error message posted
- `test_analysis_worker_cancellation()` - Can cancel mid-analysis
- `test_analysis_worker_cleanup()` - Resources cleaned up
- Mock ReconRunner to avoid actual binary analysis
- Mock asyncio.to_thread for fast tests
- Aim for >85% coverage

### Step 8: Integration Tests (2.5 hours)
Create `caspoon/tests/integration/ui/test_async_analysis.py`:
- `test_app_starts_analysis_worker()` - StartAnalysis message starts worker
- `test_app_receives_progress_updates()` - Progress updates reach app
- `test_app_state_updated_on_completion()` - AppState updated with report
- `test_app_cancels_analysis()` - Cancel message stops worker
- `test_multiple_analyses_sequential()` - Start new analysis cancels old
- `test_error_handling_integration()` - Errors handled gracefully
- `test_ui_remains_responsive()` - App responds during analysis
- Use Textual's app.run_test() with async support
- Mock ReconRunner with realistic delays (asyncio.sleep)
- Verify memory cleanup (no worker leaks)
- Aim for end-to-end validation

### Step 9: Manual Testing (1.5 hours)
Test with real binaries:
- Launch TUI: `python -m caspoon.ui`
- Load small binary (should complete quickly):
  - Verify progress updates shown
  - Verify spinner animation works
  - Verify completion notification
- Load large binary (to test progress):
  - Watch progress bar increment
  - Verify messages update
  - Verify UI stays responsive (can switch tabs, etc.)
- Test cancellation:
  - Start analysis
  - Press Ctrl+C mid-analysis
  - Verify cancellation works
  - Verify cleanup (can start new analysis)
- Test error handling:
  - Load invalid file
  - Verify error message shown
  - Verify app remains usable
- Test rapid successive analyses:
  - Start analysis
  - Immediately start new analysis
  - Verify first is cancelled, second starts

### Step 10: Documentation and Validation (30 minutes)
- Add docstrings to all worker classes and methods
- Create `caspoon/docs/guides/async-workers.md`:
  - Explain worker pattern
  - Show how to create custom workers
  - Document lifecycle and states
  - Include code examples
- Update main README with async analysis info
- Verify all tests pass: `pytest caspoon/tests/unit/ui/workers/ -v`
- Check coverage: `pytest --cov=caspoon/ui/workers --cov-report=term-missing`
- Run integration tests: `pytest caspoon/tests/integration/ui/test_async_analysis.py -v`
- Verify no regressions in existing functionality

## Code Example

```python
# caspoon/ui/workers/base.py
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


class WorkerState(Enum):
    """Worker lifecycle states."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Worker(ABC):
    """Base class for async background workers.
    
    Provides:
    - State management (idle, running, completed, failed, cancelled)
    - Progress reporting
    - Cancellation support
    - Error handling
    - Lifecycle callbacks
    
    Subclasses must implement:
    - async def run() -> Any
    
    Example:
        class MyWorker(Worker):
            async def run(self):
                self.report_progress(0, "Starting...")
                result = await asyncio.to_thread(blocking_work)
                self.report_progress(100, "Done")
                return result
            
            def on_complete(self, result):
                self.app.notify(f"Completed: {result}")
    """
    
    def __init__(self, app):
        """Initialize worker.
        
        Args:
            app: The Textual app instance
        """
        self.app = app
        self.state = WorkerState.IDLE
        self._cancelled = False
        self._task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def run(self) -> Any:
        """Execute the work. Must be implemented by subclass.
        
        Returns:
            Result of the work
        """
        pass
    
    async def start(self) -> None:
        """Start the worker asynchronously."""
        if self.state != WorkerState.IDLE:
            self.logger.warning(f"Worker already {self.state.value}")
            return
        
        self.state = WorkerState.RUNNING
        self._task = asyncio.create_task(self._run_with_error_handling())
    
    async def _run_with_error_handling(self) -> None:
        """Run with error handling wrapper."""
        try:
            result = await self.run()
            
            if not self._cancelled:
                self.state = WorkerState.COMPLETED
                self.on_complete(result)
        
        except asyncio.CancelledError:
            self.logger.info("Worker cancelled")
            self.state = WorkerState.CANCELLED
            self.on_cancel()
        
        except Exception as e:
            self.logger.error(f"Worker error: {e}", exc_info=True)
            self.state = WorkerState.FAILED
            self.on_error(e)
    
    async def cancel(self) -> None:
        """Cancel the worker gracefully."""
        if self.state != WorkerState.RUNNING:
            return
        
        self._cancelled = True
        
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        self.state = WorkerState.CANCELLED
        self.on_cancel()
    
    def report_progress(self, percent: int, message: str) -> None:
        """Report progress to app.
        
        Args:
            percent: Progress percentage (0-100)
            message: Progress message
        """
        from caspoon.ui.core.messages import ProgressUpdate
        self.app.post_message(ProgressUpdate(percent, message))
        self.logger.debug(f"Progress: {percent}% - {message}")
    
    def on_complete(self, result: Any) -> None:
        """Called on successful completion. Override to handle result.
        
        Args:
            result: The result returned by run()
        """
        self.logger.info(f"Worker completed successfully")
    
    def on_error(self, error: Exception) -> None:
        """Called on error. Override to handle error.
        
        Args:
            error: The exception that occurred
        """
        self.logger.error(f"Worker failed: {error}")
    
    def on_cancel(self) -> None:
        """Called on cancellation. Override for cleanup."""
        self.logger.info("Worker cancelled")


# caspoon/ui/workers/analysis.py
from pathlib import Path
import asyncio

from caspoon.ui.workers.base import Worker
from caspoon.recon.runner import ReconRunner


class AnalysisWorker(Worker):
    """Worker for binary analysis using ReconRunner.
    
    Runs binary analysis in background thread, reporting progress
    and updating AppState on completion.
    """
    
    def __init__(self, app, file_path: str):
        """Initialize analysis worker.
        
        Args:
            app: The Textual app instance
            file_path: Path to binary file to analyze
        """
        super().__init__(app)
        self.file_path = file_path
        self.runner: Optional[ReconRunner] = None
    
    async def run(self):
        """Run binary analysis."""
        # Validate file exists
        path = Path(self.file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        if not path.is_file():
            raise ValueError(f"Not a file: {self.file_path}")
        
        self.report_progress(10, "Loading binary...")
        
        # Initialize ReconRunner (might be blocking)
        await asyncio.sleep(0.01)  # Yield to event loop
        self.runner = ReconRunner(self.file_path)
        
        if self._cancelled:
            return None
        
        self.report_progress(30, "Extracting binary info...")
        
        # Run analysis in background thread
        report = await asyncio.to_thread(self._run_analysis_blocking)
        
        if self._cancelled:
            return None
        
        self.report_progress(100, "Analysis complete")
        return report
    
    def _run_analysis_blocking(self):
        """Run analysis (blocking). Called in thread.
        
        Returns:
            ExecutableReport
        """
        # This runs in a background thread to avoid blocking the event loop
        
        # Run the analysis
        self.runner.analyze()
        
        # Get the report
        report = self.runner.get_report()
        
        return report
    
    def on_complete(self, result) -> None:
        """Update app state with analysis results."""
        if result:
            self.app.state.update_from_report(result)
            
            from caspoon.ui.core.messages import AnalysisComplete
            self.app.post_message(AnalysisComplete(result))
            
            self.logger.info(f"Analysis completed for {self.file_path}")
    
    def on_error(self, error: Exception) -> None:
        """Post error message on analysis failure."""
        from caspoon.ui.core.messages import AnalysisError
        self.app.post_message(AnalysisError(str(error)))
        
        self.logger.error(f"Analysis failed for {self.file_path}: {error}")
    
    def on_cancel(self) -> None:
        """Cleanup on cancellation."""
        if self.runner:
            # Close runner resources if needed
            pass
        
        from caspoon.ui.core.messages import AnalysisCancelled
        self.app.post_message(AnalysisCancelled())
        
        self.logger.info(f"Analysis cancelled for {self.file_path}")
```

## Testing Strategy

### Unit Tests

**Base Worker Tests** (`test_base.py`):
- Test state initialization and transitions
- Test start/cancel methods
- Test progress reporting
- Test error handling with exceptions
- Test callbacks (on_complete, on_error, on_cancel)
- Test abstract method enforcement
- Use mock worker for testing
- Aim for >90% coverage

**AnalysisWorker Tests** (`test_analysis.py`):
- Test initialization with file path
- Test file validation (not found, not a file)
- Test analysis flow with mocked ReconRunner
- Test progress reporting at each stage
- Test completion updates state
- Test error handling
- Test cancellation mid-analysis
- Mock asyncio.to_thread for fast tests
- Aim for >85% coverage

### Integration Tests

**Async Analysis Integration** (`test_async_analysis.py`):
- Test full analysis workflow in running app
- Test progress updates reach UI
- Test state updates on completion
- Test cancellation works correctly
- Test multiple analyses (cancel old, start new)
- Test UI responsiveness during analysis
- Use app.run_test() with async
- Mock ReconRunner with delays

### Performance Tests

- Test worker overhead is minimal (<10ms)
- Test large binary analysis doesn't block UI
- Test cancellation is responsive (<100ms)

### Manual Testing

- Test with real binaries of various sizes
- Verify progress updates smooth
- Test cancellation at various stages
- Verify error messages clear
- Check memory usage (no leaks)

## Dependencies

- **Subtask 1**: Requires AppState, messages
- **Subtask 2**: Requires BaseView (for UI updates)
- **Subtask 3**: Requires CaspoonApp with AppState
- **asyncio**: Standard library
- **ReconRunner**: Existing analysis system
- **pytest-asyncio**: For async testing

## Estimated Time

**Total: 3-4 days (26-30 hours)**

Breakdown:
- Base Worker implementation: 2.5 hours
- AnalysisWorker implementation: 3 hours
- New messages: 0.5 hours
- CaspoonApp integration: 3 hours
- Status bar updates: 1.5 hours
- Base Worker tests: 2 hours
- AnalysisWorker tests: 2 hours
- Integration tests: 2.5 hours
- Manual testing: 1.5 hours
- Documentation/validation: 0.5 hours

**Buffer**: 1-2 hours for async debugging

## Success Criteria

- [ ] Worker base class implemented with state management
- [ ] Worker state transitions work correctly (idle → running → completed/failed/cancelled)
- [ ] AnalysisWorker runs binary analysis in background
- [ ] AnalysisWorker reports progress at multiple stages
- [ ] UI remains responsive during analysis (can interact with app)
- [ ] Progress shown in status bar or footer (percent and message)
- [ ] Cancellation works (Ctrl+C stops analysis gracefully)
- [ ] AppState updated on successful analysis completion
- [ ] Error messages displayed on analysis failure
- [ ] Worker unit tests pass (minimum 18 tests)
- [ ] Integration tests pass (minimum 7 tests)
- [ ] Test coverage >85% for workers module
- [ ] No memory leaks (worker cleanup verified)
- [ ] Manual testing shows smooth progress updates
- [ ] Can load large binary without UI freeze
- [ ] Multiple successive analyses work correctly
- [ ] Documentation complete with examples

## Next Steps

After completing this subtask:
1. **Non-Blocking UI Achieved**: Can now analyze binaries without freezing
2. **Proceed to Subtask 6**: Implement command palette for keyboard-driven workflows
3. **Proceed to Subtask 7**: Add multi-panel layout for advanced UX
4. **Future Workers**: Pattern established for other async operations (export, diff, etc.)
5. **Performance Optimization**: Fine-tune progress reporting and threading
