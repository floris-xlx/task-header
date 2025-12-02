"""
Sticky header widget that displays the current issue at the top of the screen.
Always stays on top and cannot be covered by other windows.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QApplication, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QTimer, QEvent
from PyQt6.QtGui import QFont, QScreen, QEnterEvent
from typing import Optional, Dict, Any, List, Callable


class StickyHeaderWidget(QWidget):
    """Always-on-top widget displaying the current issue."""
    
    def __init__(self, config, linear_client=None):
        """
        Initialize sticky header widget.
        
        Args:
            config: Config instance
            linear_client: LinearClient instance (optional)
        """
        super().__init__()
        self.config = config
        self.linear_client = linear_client
        self.current_issue: Optional[Dict[str, Any]] = None
        self.workflow_states: List[Dict[str, Any]] = []
        self.on_state_changed: Optional[Callable] = None
        self.controls_visible = False
        
        self._init_ui()
        self._position_window()
        self._apply_appearance()
        
        # Load current issue if set
        if self.config.current_issue_id and self.linear_client:
            self.load_issue(self.config.current_issue_id)
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Set window flags for always-on-top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Make window semi-transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Top bar with controls
        top_bar = QHBoxLayout()
        
        # Close button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                background-color: #c42b1c;
            }
            QPushButton:hover {
                background-color: #a0210f;
            }
        """)
        self.close_btn.clicked.connect(self.hide)
        
        # Settings button
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.clicked.connect(self._open_settings)
        
        top_bar.addWidget(self.settings_btn)
        top_bar.addStretch()
        top_bar.addWidget(self.close_btn)
        
        layout.addLayout(top_bar)
        
        # Issue title label
        self.title_label = QLabel("No issue selected")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        title_font = QFont()
        title_font.setPointSize(self.config.font_size)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
        
        # Issue identifier label
        self.identifier_label = QLabel("")
        self.identifier_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        identifier_font = QFont()
        identifier_font.setPointSize(12)
        self.identifier_label.setFont(identifier_font)
        self.identifier_label.setStyleSheet("color: #888888;")
        layout.addWidget(self.identifier_label)
        
        # Status controls
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Status:")
        status_font = QFont()
        status_font.setPointSize(14)
        self.status_label.setFont(status_font)
        
        self.status_combo = QComboBox()
        self.status_combo.setFont(status_font)
        self.status_combo.currentIndexChanged.connect(self._on_status_changed)
        
        status_layout.addStretch()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        
        self.setLayout(layout)
        
        # Enable mouse tracking for this widget and all children
        self.setMouseTracking(True)
        for child in self.findChildren(QWidget):
            child.setMouseTracking(True)
        
        # Initially hide controls
        self._hide_controls()
    
    def _position_window(self):
        """Position window at top-middle of screen."""
        screen: QScreen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        
        # Use header_width for the sticky header width
        width_percent = self.config.get("window.header_width", 50)
        height_percent = self.config.get("window.height_percent", 10)
        
        width = int(screen_geometry.width() * width_percent / 100)
        height = int(screen_geometry.height() * height_percent / 100)
        
        # Ensure minimum size
        width = max(width, 400)
        height = max(height, 150)
        
        x = (screen_geometry.width() - width) // 2
        y = 0  # Top of screen
        
        self.setGeometry(x, y, width, height)
    
    def _open_settings(self):
        """Open settings/navigation window."""
        # This will be handled by the main application
        if hasattr(self, 'on_settings_clicked'):
            self.on_settings_clicked()
    
    def load_issue(self, issue_id: str):
        """
        Load and display an issue.
        
        Args:
            issue_id: Issue ID to load
        """
        if not self.linear_client:
            self.title_label.setText("Linear API not configured")
            return
        
        try:
            issue = self.linear_client.get_issue(issue_id)
            self.current_issue = issue
            self._display_issue(issue)
            
            # Save current issue
            self.config.current_issue_id = issue_id
            self.config.save()
            
            # Load workflow states for the team
            if issue.get("team", {}).get("id"):
                self._load_workflow_states(issue["team"]["id"])
            
        except Exception as e:
            self.title_label.setText(f"Error loading issue: {str(e)}")
            print(f"Error loading issue: {e}")
    
    def _display_issue(self, issue: Dict[str, Any]):
        """
        Display issue in the widget.
        
        Args:
            issue: Issue data
        """
        title = issue.get("title", "No title")
        identifier = issue.get("identifier", "")
        state = issue.get("state", {})
        
        self.title_label.setText(title)
        self.identifier_label.setText(identifier)
        
        # Update status combo
        if state:
            self._update_status_combo(state)
    
    def _load_workflow_states(self, team_id: str):
        """
        Load workflow states for a team.
        
        Args:
            team_id: Team ID
        """
        try:
            self.workflow_states = self.linear_client.get_workflow_states(team_id)
            self._populate_status_combo()
        except Exception as e:
            print(f"Error loading workflow states: {e}")
    
    def _populate_status_combo(self):
        """Populate status combo box with workflow states."""
        self.status_combo.blockSignals(True)
        self.status_combo.clear()
        
        for state in self.workflow_states:
            self.status_combo.addItem(state["name"], state["id"])
        
        # Set current state
        if self.current_issue and self.current_issue.get("state"):
            current_state_id = self.current_issue["state"]["id"]
            index = self.status_combo.findData(current_state_id)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        
        self.status_combo.blockSignals(False)
    
    def _update_status_combo(self, state: Dict[str, Any]):
        """
        Update status combo to show current state.
        
        Args:
            state: Current state data
        """
        if not self.workflow_states:
            self.status_combo.blockSignals(True)
            self.status_combo.clear()
            self.status_combo.addItem(state.get("name", "Unknown"), state.get("id"))
            self.status_combo.blockSignals(False)
        else:
            state_id = state.get("id")
            index = self.status_combo.findData(state_id)
            if index >= 0:
                self.status_combo.blockSignals(True)
                self.status_combo.setCurrentIndex(index)
                self.status_combo.blockSignals(False)
    
    def _on_status_changed(self, index: int):
        """Handle status change."""
        if not self.current_issue or not self.linear_client:
            return
        
        state_id = self.status_combo.itemData(index)
        if not state_id:
            return
        
        try:
            result = self.linear_client.update_issue_state(
                self.current_issue["id"],
                state_id
            )
            
            if result.get("success"):
                print(f"Issue state updated successfully")
                # Notify callback
                if self.on_state_changed:
                    self.on_state_changed(self.current_issue["id"], state_id)
            else:
                print("Failed to update issue state")
                
        except Exception as e:
            print(f"Error updating issue state: {e}")
    
    def set_custom_task(self, title: str):
        """
        Display a custom task (not from Linear).
        
        Args:
            title: Task title
        """
        self.current_issue = None
        self.title_label.setText(title)
        self.identifier_label.setText("Custom Task")
        self.status_combo.clear()
        self.status_combo.addItem("Active", "active")
        self.status_combo.addItem("Completed", "completed")
    
    def clear(self):
        """Clear the current issue display."""
        self.current_issue = None
        self.title_label.setText("No issue selected")
        self.identifier_label.setText("")
        self.status_combo.clear()
        self.config.current_issue_id = None
        self.config.save()
    
    def _apply_appearance(self):
        """Apply transparency and styling to the window."""
        transparency = self.config.get("window.transparency", 100)
        
        # Calculate opacity (0.0 to 1.0)
        opacity = transparency / 100.0
        
        # Calculate RGB with transparency for background
        # Use RGBA format in stylesheet
        alpha = int(255 * opacity)
        
        # Text should never go below 10% opacity (26/255)
        text_alpha = max(26, alpha)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(30, 30, 30, {alpha});
                color: rgba(255, 255, 255, {text_alpha});
                border: 2px solid rgba(0, 122, 204, {alpha});
                border-radius: 8px;
            }}
            QLabel {{
                background-color: transparent;
                border: none;
                color: rgba(255, 255, 255, {text_alpha});
            }}
            QPushButton {{
                background-color: rgba(0, 122, 204, {alpha});
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                color: rgba(255, 255, 255, {text_alpha});
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 90, 158, {alpha});
            }}
            QPushButton:pressed {{
                background-color: rgba(0, 69, 120, {alpha});
            }}
            QComboBox {{
                background-color: rgba(45, 45, 45, {alpha});
                border: 1px solid rgba(0, 122, 204, {alpha});
                border-radius: 4px;
                padding: 5px;
                color: rgba(255, 255, 255, {text_alpha});
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid rgba(255, 255, 255, {text_alpha});
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: rgba(45, 45, 45, 255);
                color: rgba(255, 255, 255, 255);
                selection-background-color: rgba(0, 122, 204, 255);
            }}
        """)
        
        # Reposition window with new width
        self._position_window()
    
    def _hide_controls(self):
        """Hide status, close button, and settings button."""
        self.close_btn.hide()
        self.settings_btn.hide()
        self.status_label.hide()
        self.status_combo.hide()
        self.controls_visible = False
    
    def _show_controls(self):
        """Show status, close button, and settings button."""
        self.close_btn.show()
        self.settings_btn.show()
        self.status_label.show()
        self.status_combo.show()
        self.controls_visible = True
    
    def enterEvent(self, event: QEnterEvent):
        """Handle mouse entering the widget."""
        if not self.controls_visible:
            self._show_controls()
        super().enterEvent(event)
    
    def leaveEvent(self, event: QEvent):
        """Handle mouse leaving the widget."""
        if self.controls_visible:
            self._hide_controls()
        super().leaveEvent(event)
    
    def event(self, event: QEvent) -> bool:
        """Handle all events to catch mouse position."""
        if event.type() == QEvent.Type.MouseMove:
            # Check if mouse is within widget bounds
            if self.rect().contains(self.mapFromGlobal(self.cursor().pos())):
                if not self.controls_visible:
                    self._show_controls()
            else:
                if self.controls_visible:
                    self._hide_controls()
        return super().event(event)
    
    def update_appearance(self):
        """Update appearance settings (called from settings)."""
        self._apply_appearance()

