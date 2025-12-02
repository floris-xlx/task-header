"""
Main entry point for the Linear Task Header application.
"""

import sys
import keyboard
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer

from config import Config
from linear_client import LinearClient
from sticky_header import StickyHeaderWidget
from navigation_window import NavigationWindow


class LinearTaskHeaderApp:
    """Main application coordinator."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = Config()
        self.linear_client = None
        self.app = QApplication(sys.argv)
        
        # Initialize Linear client if API key exists
        if self.config.linear_api_key:
            try:
                self.linear_client = LinearClient(self.config.linear_api_key)
            except Exception as e:
                print(f"Error initializing Linear client: {e}")
        
        # Create windows
        self.sticky_header = StickyHeaderWidget(self.config, self.linear_client)
        self.navigation_window = NavigationWindow(self.config, self.linear_client)
        
        # Connect signals
        self._connect_signals()
        
        # Setup hotkey
        self._setup_hotkey()
        
        # Show sticky header if there's a current issue
        if self.config.current_issue_id:
            self.sticky_header.show()
    
    def _connect_signals(self):
        """Connect signals between components."""
        # When issue is selected in navigation, update sticky header
        self.navigation_window.issue_selected.connect(self._on_issue_selected)
        
        # When settings button is clicked on sticky header, show navigation
        self.sticky_header.on_settings_clicked = self._show_navigation
        
        # Handle custom task
        self.navigation_window.on_custom_task = self._on_custom_task
        
        # Handle state changes in sticky header
        self.sticky_header.on_state_changed = self._on_state_changed
        
        # Handle settings applied
        self.navigation_window.on_settings_applied = self._on_settings_applied
    
    def _setup_hotkey(self):
        """Setup global hotkey for toggling navigation window."""
        hotkey = self.config.hotkey
        
        try:
            # Register hotkey
            keyboard.add_hotkey(hotkey, self._toggle_navigation)
            print(f"Hotkey registered: {hotkey}")
        except Exception as e:
            print(f"Error registering hotkey {hotkey}: {e}")
            # Try default if custom hotkey fails
            if hotkey != "ctrl+w":
                try:
                    keyboard.add_hotkey("ctrl+w", self._toggle_navigation)
                    print("Registered default hotkey: ctrl+w")
                except Exception as e2:
                    print(f"Error registering default hotkey: {e2}")
    
    def _toggle_navigation(self):
        """Toggle navigation window visibility."""
        # Use QTimer to ensure thread-safe GUI operations
        QTimer.singleShot(0, self._toggle_navigation_gui)
    
    def _toggle_navigation_gui(self):
        """Toggle navigation window (GUI thread safe)."""
        if self.navigation_window.isVisible():
            self.navigation_window.hide()
        else:
            self.navigation_window.show()
            self.navigation_window.activateWindow()
            self.navigation_window.raise_()
    
    def _show_navigation(self):
        """Show navigation window."""
        self.navigation_window.show()
        self.navigation_window.activateWindow()
        self.navigation_window.raise_()
    
    def _on_issue_selected(self, issue_id: str):
        """
        Handle issue selection.
        
        Args:
            issue_id: Selected issue ID
        """
        if not self.linear_client:
            # Try to initialize Linear client
            if self.config.linear_api_key:
                try:
                    self.linear_client = LinearClient(self.config.linear_api_key)
                    self.sticky_header.linear_client = self.linear_client
                except Exception as e:
                    QMessageBox.critical(
                        self.navigation_window,
                        "Error",
                        f"Failed to initialize Linear client: {str(e)}"
                    )
                    return
            else:
                QMessageBox.warning(
                    self.navigation_window,
                    "Error",
                    "Please configure Linear API key first"
                )
                return
        
        # Update Linear client reference in case it was just created
        self.sticky_header.linear_client = self.linear_client
        
        # Load issue in sticky header
        self.sticky_header.load_issue(issue_id)
        self.sticky_header.show()
    
    def _on_custom_task(self, task: str):
        """
        Handle custom task creation.
        
        Args:
            task: Custom task description
        """
        self.sticky_header.set_custom_task(task)
        self.sticky_header.show()
    
    def _on_state_changed(self, issue_id: str, state_id: str):
        """
        Handle issue state change.
        
        Args:
            issue_id: Issue ID
            state_id: New state ID
        """
        print(f"Issue {issue_id} state changed to {state_id}")
        # Could trigger markdown regeneration here if needed
    
    def _on_settings_applied(self):
        """Handle settings being applied from navigation window."""
        # Update sticky header appearance
        self.sticky_header.update_appearance()
        print("Header appearance updated")
    
    def run(self):
        """Run the application."""
        print("Linear Task Header Application Started")
        print(f"Hotkey: {self.config.hotkey}")
        print("Press the hotkey to toggle navigation window")
        
        # Show navigation window initially if no issue is set
        if not self.config.current_issue_id:
            self.navigation_window.show()
        
        return self.app.exec()
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            # Unhook all hotkeys
            keyboard.unhook_all()
        except Exception as e:
            print(f"Error during cleanup: {e}")


def main():
    """Main entry point."""
    try:
        app = LinearTaskHeaderApp()
        exit_code = app.run()
        app.cleanup()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

