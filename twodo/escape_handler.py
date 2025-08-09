#!/usr/bin/env python3
"""
Escape Key Handler - Global escape key listener for 2do CLI
Provides immediate interruption of running tasks when Escape is pressed
"""

import sys
import threading
import time
import signal
from contextlib import contextmanager
from rich.console import Console

console = Console()

class EscapeHandler:
    """Global escape key handler for immediate task interruption"""
    
    def __init__(self):
        self.interrupted = False
        self.listener_thread = None
        self.original_sigint_handler = None
        self._stop_listening = False
        
    def _keyboard_listener(self):
        """Listen for keyboard input in a separate thread"""
        try:
            import termios
            import tty
            import select
            
            # Save original terminal settings
            if sys.stdin.isatty():
                old_settings = termios.tcgetattr(sys.stdin)
                tty.setraw(sys.stdin.fileno())
                
                try:
                    while not self._stop_listening:
                        # Check if input is available
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            char = sys.stdin.read(1)
                            # Check for Escape key (ASCII 27)
                            if ord(char) == 27:
                                self.interrupted = True
                                console.print("\n⚠️ Escape key pressed - interrupting current operation...")
                                break
                        time.sleep(0.05)  # Small delay to prevent high CPU usage
                        
                finally:
                    # Restore terminal settings
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    
        except (ImportError, OSError):
            # Fallback for systems without termios (Windows) or non-TTY environments
            self._fallback_listener()
    
    def _fallback_listener(self):
        """Fallback listener for systems without termios support"""
        try:
            import msvcrt  # Windows
            while not self._stop_listening:
                if msvcrt.kbhit():
                    char = msvcrt.getch()
                    if ord(char) == 27:  # Escape key
                        self.interrupted = True
                        console.print("\n⚠️ Escape key pressed - interrupting current operation...")
                        break
                time.sleep(0.05)
        except ImportError:
            # No keyboard support available, just wait for stop signal
            while not self._stop_listening:
                time.sleep(0.1)
    
    def _signal_handler(self, signum, frame):
        """Handle SIGINT (Ctrl+C) as well as Escape"""
        self.interrupted = True
        console.print("\n⚠️ Interrupt signal received - stopping current operation...")
        
        # Call original handler if it exists
        if self.original_sigint_handler and callable(self.original_sigint_handler):
            self.original_sigint_handler(signum, frame)
    
    def start_listening(self):
        """Start listening for escape key in background thread"""
        if self.listener_thread and self.listener_thread.is_alive():
            return  # Already listening
            
        self.interrupted = False
        self._stop_listening = False
        
        # Set up signal handler for Ctrl+C
        self.original_sigint_handler = signal.signal(signal.SIGINT, self._signal_handler)
        
        # Start keyboard listener thread
        self.listener_thread = threading.Thread(target=self._keyboard_listener, daemon=True)
        self.listener_thread.start()
    
    def stop_listening(self):
        """Stop listening for escape key"""
        self._stop_listening = True
        
        # Restore original signal handler
        if self.original_sigint_handler:
            signal.signal(signal.SIGINT, self.original_sigint_handler)
            self.original_sigint_handler = None
        
        # Wait for listener thread to finish
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=1.0)
    
    def is_interrupted(self):
        """Check if operation was interrupted"""
        return self.interrupted
    
    def reset(self):
        """Reset interrupt state"""
        self.interrupted = False

# Global instance
_global_escape_handler = EscapeHandler()

@contextmanager
def escape_listener():
    """Context manager for escape key listening during operations"""
    _global_escape_handler.reset()
    _global_escape_handler.start_listening()
    
    try:
        yield _global_escape_handler
    finally:
        _global_escape_handler.stop_listening()

def check_escape_interrupt():
    """Quick check if escape was pressed (for polling in loops)"""
    return _global_escape_handler.is_interrupted()

def reset_escape_state():
    """Reset the global escape state"""
    _global_escape_handler.reset()

class EscapeInterrupt(Exception):
    """Exception raised when operation is interrupted by escape key"""
    pass

def raise_if_interrupted():
    """Raise EscapeInterrupt if escape key was pressed"""
    if _global_escape_handler.is_interrupted():
        raise EscapeInterrupt("Operation interrupted by escape key")
