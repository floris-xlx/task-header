"""
Navigation window for browsing Linear teams, projects, and issues.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QTabWidget, QMessageBox, QInputDialog, QTextEdit, QSlider, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, Dict, Any, List


class NavigationWindow(QMainWindow):
    """Main window for navigating Linear data."""
    
    issue_selected = pyqtSignal(str)  # Emits issue ID when selected
    
    def __init__(self, config, linear_client=None):
        """
        Initialize navigation window.
        
        Args:
            config: Config instance
            linear_client: LinearClient instance (optional)
        """
        super().__init__()
        self.config = config
        self.linear_client = linear_client
        self.current_team: Optional[Dict[str, Any]] = None
        self.current_project: Optional[Dict[str, Any]] = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Linear Task Navigator")
        self.setMinimumSize(800, 600)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #007acc;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QPushButton:disabled {
                background-color: #3e3e3e;
                color: #888888;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #007acc;
                border-radius: 4px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #007acc;
                border-radius: 4px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                color: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3e3e3e;
            }
            QListWidget::item:selected {
                background-color: #007acc;
            }
            QListWidget::item:hover {
                background-color: #2a2a2a;
            }
            QTabWidget::pane {
                border: 1px solid #3e3e3e;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: white;
                padding: 8px 16px;
                border: 1px solid #3e3e3e;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
            }
            QTabBar::tab:hover {
                background-color: #3e3e3e;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # API Key section
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel("Linear API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter your Linear API key")
        
        if self.config.linear_api_key:
            self.api_key_input.setText(self.config.linear_api_key)
        
        self.save_api_key_btn = QPushButton("Save API Key")
        self.save_api_key_btn.clicked.connect(self._save_api_key)
        
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input, 1)
        api_key_layout.addWidget(self.save_api_key_btn)
        
        layout.addLayout(api_key_layout)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Connect tab change event for instant refresh
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        # Teams tab
        self.teams_tab = self._create_teams_tab()
        self.tab_widget.addTab(self.teams_tab, "Teams")
        
        # Projects tab
        self.projects_tab = self._create_projects_tab()
        self.tab_widget.addTab(self.projects_tab, "Projects")
        
        # Issues tab
        self.issues_tab = self._create_issues_tab()
        self.tab_widget.addTab(self.issues_tab, "Issues")
        
        # My Issues tab
        self.my_issues_tab = self._create_my_issues_tab()
        self.tab_widget.addTab(self.my_issues_tab, "My Issues")
        
        # Custom Task tab
        self.custom_task_tab = self._create_custom_task_tab()
        self.tab_widget.addTab(self.custom_task_tab, "Custom Task")
        
        # Settings tab
        self.settings_tab = self._create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        layout.addWidget(self.tab_widget)
        
        central_widget.setLayout(layout)
    
    def _create_teams_tab(self) -> QWidget:
        """Create teams tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Teams")
        refresh_btn.clicked.connect(self._load_teams)
        layout.addWidget(refresh_btn)
        
        # Teams list
        self.teams_list = QListWidget()
        self.teams_list.itemDoubleClicked.connect(self._on_team_selected)
        layout.addWidget(self.teams_list)
        
        # Select button
        select_team_btn = QPushButton("View Team Issues")
        select_team_btn.clicked.connect(self._view_team_issues)
        layout.addWidget(select_team_btn)
        
        widget.setLayout(layout)
        return widget
    
    def _create_projects_tab(self) -> QWidget:
        """Create projects tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Info label
        self.projects_info_label = QLabel("Select a team first")
        layout.addWidget(self.projects_info_label)
        
        # Refresh button
        refresh_projects_btn = QPushButton("Refresh Projects")
        refresh_projects_btn.clicked.connect(self._load_projects)
        layout.addWidget(refresh_projects_btn)
        
        # Projects list
        self.projects_list = QListWidget()
        self.projects_list.itemDoubleClicked.connect(self._on_project_selected)
        layout.addWidget(self.projects_list)
        
        # Select button
        select_project_btn = QPushButton("View Project Issues")
        select_project_btn.clicked.connect(self._view_project_issues)
        layout.addWidget(select_project_btn)
        
        widget.setLayout(layout)
        return widget
    
    def _create_issues_tab(self) -> QWidget:
        """Create issues tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Info label
        self.issues_info_label = QLabel("Select a team or project first")
        layout.addWidget(self.issues_info_label)
        
        # Issues list
        self.issues_list = QListWidget()
        self.issues_list.itemDoubleClicked.connect(self._on_issue_selected)
        layout.addWidget(self.issues_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        set_active_btn = QPushButton("Set as Active Issue")
        set_active_btn.clicked.connect(self._set_active_issue)
        btn_layout.addWidget(set_active_btn)
        
        create_issue_btn = QPushButton("Create New Issue")
        create_issue_btn.clicked.connect(self._create_issue)
        btn_layout.addWidget(create_issue_btn)
        
        layout.addLayout(btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    def _create_my_issues_tab(self) -> QWidget:
        """Create my issues tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Refresh button
        refresh_my_issues_btn = QPushButton("Refresh My Issues")
        refresh_my_issues_btn.clicked.connect(self._load_my_issues)
        layout.addWidget(refresh_my_issues_btn)
        
        # My issues list
        self.my_issues_list = QListWidget()
        self.my_issues_list.itemDoubleClicked.connect(self._on_my_issue_selected)
        layout.addWidget(self.my_issues_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        set_active_my_btn = QPushButton("Set as Active Issue")
        set_active_my_btn.clicked.connect(self._set_active_my_issue)
        btn_layout.addWidget(set_active_my_btn)
        
        generate_md_btn = QPushButton("Generate my-issues.md")
        generate_md_btn.clicked.connect(self._generate_my_issues_md)
        btn_layout.addWidget(generate_md_btn)
        
        layout.addLayout(btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    def _create_custom_task_tab(self) -> QWidget:
        """Create custom task tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel("Create a custom task that's not in Linear:")
        layout.addWidget(instructions)
        
        # Task input
        self.custom_task_input = QLineEdit()
        self.custom_task_input.setPlaceholderText("Enter task description")
        layout.addWidget(self.custom_task_input)
        
        # Create button
        create_custom_btn = QPushButton("Set as Active Task")
        create_custom_btn.clicked.connect(self._set_custom_task)
        layout.addWidget(create_custom_btn)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _create_settings_tab(self) -> QWidget:
        """Create settings tab for appearance customization."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Header width setting
        width_group = QVBoxLayout()
        width_label = QLabel("Header Width (% of screen):")
        width_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        width_group.addWidget(width_label)
        
        width_layout = QHBoxLayout()
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setMinimum(10)
        self.width_slider.setMaximum(100)
        self.width_slider.setValue(self.config.get("window.header_width", 50))
        self.width_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.width_slider.setTickInterval(10)
        
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setMinimum(10)
        self.width_spinbox.setMaximum(100)
        self.width_spinbox.setValue(self.config.get("window.header_width", 50))
        self.width_spinbox.setSuffix("%")
        
        # Connect slider and spinbox
        self.width_slider.valueChanged.connect(self.width_spinbox.setValue)
        self.width_spinbox.valueChanged.connect(self.width_slider.setValue)
        self.width_slider.valueChanged.connect(self._on_width_changed)
        
        width_layout.addWidget(self.width_slider, 3)
        width_layout.addWidget(self.width_spinbox, 1)
        width_group.addLayout(width_layout)
        
        layout.addLayout(width_group)
        
        # Transparency setting
        transparency_group = QVBoxLayout()
        transparency_label = QLabel("Background Transparency:")
        transparency_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        transparency_group.addWidget(transparency_label)
        
        transparency_layout = QHBoxLayout()
        self.transparency_slider = QSlider(Qt.Orientation.Horizontal)
        self.transparency_slider.setMinimum(0)
        self.transparency_slider.setMaximum(100)
        self.transparency_slider.setValue(self.config.get("window.transparency", 100))
        self.transparency_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.transparency_slider.setTickInterval(10)
        
        self.transparency_spinbox = QSpinBox()
        self.transparency_spinbox.setMinimum(0)
        self.transparency_spinbox.setMaximum(100)
        self.transparency_spinbox.setValue(self.config.get("window.transparency", 100))
        self.transparency_spinbox.setSuffix("%")
        
        # Connect slider and spinbox
        self.transparency_slider.valueChanged.connect(self.transparency_spinbox.setValue)
        self.transparency_spinbox.valueChanged.connect(self.transparency_slider.setValue)
        self.transparency_slider.valueChanged.connect(self._on_transparency_changed)
        
        transparency_layout.addWidget(self.transparency_slider, 3)
        transparency_layout.addWidget(self.transparency_spinbox, 1)
        transparency_group.addLayout(transparency_layout)
        
        transparency_hint = QLabel("0% = fully transparent, 100% = fully opaque")
        transparency_hint.setStyleSheet("color: #888888; font-size: 12px;")
        transparency_group.addWidget(transparency_hint)
        
        layout.addLayout(transparency_group)
        
        # Apply button
        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self._apply_settings)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _save_api_key(self):
        """Save API key to configuration."""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "Error", "Please enter an API key")
            return
        
        self.config.linear_api_key = api_key
        self.config.save()
        
        # Update Linear client
        from linear_client import LinearClient
        self.linear_client = LinearClient(api_key)
        
        # Instant refresh: reload current tab content
        self._refresh_current_tab()
        
        QMessageBox.information(self, "Success", "API key saved successfully")
    
    def _load_teams(self):
        """Load teams from Linear."""
        if not self.linear_client:
            QMessageBox.warning(self, "Error", "Please configure Linear API key first")
            return
        
        try:
            teams = self.linear_client.get_teams()
            self.teams_list.clear()
            
            for team in teams:
                item = QListWidgetItem(f"{team['name']} ({team['key']})")
                item.setData(Qt.ItemDataRole.UserRole, team)
                self.teams_list.addItem(item)
            
            QMessageBox.information(self, "Success", f"Loaded {len(teams)} teams")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load teams: {str(e)}")
    
    def _on_team_selected(self, item: QListWidgetItem):
        """Handle team selection."""
        team = item.data(Qt.ItemDataRole.UserRole)
        self.current_team = team
        self.projects_info_label.setText(f"Team: {team['name']}")
        
        # Instant refresh: load projects for the selected team
        self._load_projects_silently()
    
    def _view_team_issues(self):
        """View issues for the selected team."""
        item = self.teams_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Please select a team")
            return
        
        team = item.data(Qt.ItemDataRole.UserRole)
        self.current_team = team
        self.current_project = None
        
        try:
            issues = self.linear_client.get_team_issues(team['id'])
            self._display_issues(issues, f"Team: {team['name']}")
            self.tab_widget.setCurrentWidget(self.issues_tab)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load issues: {str(e)}")
    
    def _load_projects(self):
        """Load projects for the selected team."""
        if not self.current_team:
            QMessageBox.warning(self, "Error", "Please select a team first")
            return
        
        if not self.linear_client:
            QMessageBox.warning(self, "Error", "Please configure Linear API key first")
            return
        
        try:
            projects = self.linear_client.get_team_projects(self.current_team['id'])
            self.projects_list.clear()
            
            for project in projects:
                item = QListWidgetItem(f"{project['name']} - {project.get('state', 'N/A')}")
                item.setData(Qt.ItemDataRole.UserRole, project)
                self.projects_list.addItem(item)
            
            QMessageBox.information(self, "Success", f"Loaded {len(projects)} projects")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load projects: {str(e)}")
    
    def _on_project_selected(self, item: QListWidgetItem):
        """Handle project selection."""
        project = item.data(Qt.ItemDataRole.UserRole)
        self.current_project = project
        
        # Instant refresh: load issues for the selected project
        self._view_project_issues_silently()
    
    def _view_project_issues(self):
        """View issues for the selected project."""
        item = self.projects_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Please select a project")
            return
        
        project = item.data(Qt.ItemDataRole.UserRole)
        self.current_project = project
        
        try:
            issues = self.linear_client.get_project_issues(project['id'])
            self._display_issues(issues, f"Project: {project['name']}")
            self.tab_widget.setCurrentWidget(self.issues_tab)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load issues: {str(e)}")
    
    def _display_issues(self, issues: List[Dict[str, Any]], info: str):
        """Display issues in the issues list (excluding done issues)."""
        self.issues_info_label.setText(info)
        self.issues_list.clear()
        
        # Filter out done/completed issues
        filtered_issues = [
            issue for issue in issues 
            if issue.get('state', {}).get('type', '').lower() not in ['completed', 'canceled']
        ]
        
        for issue in filtered_issues:
            state_name = issue.get('state', {}).get('name', 'Unknown')
            item_text = f"{issue['identifier']}: {issue['title']} [{state_name}]"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, issue)
            self.issues_list.addItem(item)
    
    def _on_issue_selected(self, item: QListWidgetItem):
        """Handle issue double-click."""
        issue = item.data(Qt.ItemDataRole.UserRole)
        self.issue_selected.emit(issue['id'])
    
    def _set_active_issue(self):
        """Set the selected issue as active."""
        item = self.issues_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Please select an issue")
            return
        
        issue = item.data(Qt.ItemDataRole.UserRole)
        self.issue_selected.emit(issue['id'])
        QMessageBox.information(self, "Success", f"Set {issue['identifier']} as active issue")
    
    def _load_my_issues(self):
        """Load issues assigned to the current user (excluding done issues)."""
        if not self.linear_client:
            QMessageBox.warning(self, "Error", "Please configure Linear API key first")
            return
        
        try:
            issues = self.linear_client.get_my_issues()
            self.my_issues_list.clear()
            
            # Filter out done/completed issues
            filtered_issues = [
                issue for issue in issues 
                if issue.get('state', {}).get('type', '').lower() not in ['completed', 'canceled']
            ]
            
            for issue in filtered_issues:
                state_name = issue.get('state', {}).get('name', 'Unknown')
                team_key = issue.get('team', {}).get('key', 'N/A')
                item_text = f"[{team_key}] {issue['identifier']}: {issue['title']} [{state_name}]"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, issue)
                self.my_issues_list.addItem(item)
            
            QMessageBox.information(self, "Success", f"Loaded {len(filtered_issues)} active issues (done issues hidden)")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load issues: {str(e)}")
    
    def _on_my_issue_selected(self, item: QListWidgetItem):
        """Handle my issue double-click."""
        issue = item.data(Qt.ItemDataRole.UserRole)
        self.issue_selected.emit(issue['id'])
    
    def _set_active_my_issue(self):
        """Set the selected issue from my issues as active."""
        item = self.my_issues_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Please select an issue")
            return
        
        issue = item.data(Qt.ItemDataRole.UserRole)
        self.issue_selected.emit(issue['id'])
        QMessageBox.information(self, "Success", f"Set {issue['identifier']} as active issue")
    
    def _generate_my_issues_md(self):
        """Generate markdown file for my issues."""
        if not self.linear_client:
            QMessageBox.warning(self, "Error", "Please configure Linear API key first")
            return
        
        try:
            from markdown_sync import MarkdownSync
            
            issues = self.linear_client.get_my_issues()
            sync = MarkdownSync(self.config, self.linear_client)
            filepath = sync.generate_my_issues_md(issues)
            
            QMessageBox.information(self, "Success", f"Generated: {filepath}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate markdown: {str(e)}")
    
    def _create_issue(self):
        """Create a new issue in Linear."""
        if not self.linear_client:
            QMessageBox.warning(self, "Error", "Please configure Linear API key first")
            return
        
        if not self.current_team:
            QMessageBox.warning(self, "Error", "Please select a team first")
            return
        
        # Get title
        title, ok = QInputDialog.getText(self, "Create Issue", "Issue Title:")
        if not ok or not title:
            return
        
        # Get description
        description, ok = QInputDialog.getMultiLineText(self, "Create Issue", "Description (optional):")
        if not ok:
            description = ""
        
        try:
            result = self.linear_client.create_issue(
                self.current_team['id'],
                title,
                description
            )
            
            if result.get('success'):
                issue = result.get('issue', {})
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Created issue: {issue.get('identifier', 'Unknown')}"
                )
                
                # Refresh issues list
                self._view_team_issues()
            else:
                QMessageBox.warning(self, "Error", "Failed to create issue")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create issue: {str(e)}")
    
    def _set_custom_task(self):
        """Set a custom task as active."""
        task = self.custom_task_input.text().strip()
        
        if not task:
            QMessageBox.warning(self, "Error", "Please enter a task description")
            return
        
        # Emit a signal with None to indicate custom task
        # The main app will handle this differently
        if hasattr(self, 'on_custom_task'):
            self.on_custom_task(task)
        
        QMessageBox.information(self, "Success", "Custom task set as active")
    
    def _on_tab_changed(self, index: int):
        """Handle tab change event for instant refresh."""
        if not self.linear_client:
            return
        
        # Get the current tab widget
        current_tab = self.tab_widget.currentWidget()
        
        try:
            # Auto-refresh based on which tab is opened
            if current_tab == self.teams_tab:
                self._load_teams_silently()
            elif current_tab == self.projects_tab:
                if self.current_team:
                    self._load_projects_silently()
            elif current_tab == self.issues_tab:
                # Refresh issues if we have a context
                if self.current_project:
                    self._view_project_issues_silently()
                elif self.current_team:
                    self._view_team_issues_silently()
            elif current_tab == self.my_issues_tab:
                self._load_my_issues_silently()
        except Exception as e:
            # Silent refresh - don't show error popups
            print(f"Auto-refresh error: {e}")
    
    def _refresh_current_tab(self):
        """Refresh the content of the currently active tab."""
        current_index = self.tab_widget.currentIndex()
        self._on_tab_changed(current_index)
    
    def _load_teams_silently(self):
        """Load teams without showing success popup."""
        if not self.linear_client:
            return
        
        try:
            teams = self.linear_client.get_teams()
            self.teams_list.clear()
            
            for team in teams:
                item = QListWidgetItem(f"{team['name']} ({team['key']})")
                item.setData(Qt.ItemDataRole.UserRole, team)
                self.teams_list.addItem(item)
        except Exception as e:
            print(f"Failed to load teams: {e}")
    
    def _load_projects_silently(self):
        """Load projects without showing success popup."""
        if not self.current_team or not self.linear_client:
            return
        
        try:
            projects = self.linear_client.get_team_projects(self.current_team['id'])
            self.projects_list.clear()
            
            for project in projects:
                item = QListWidgetItem(f"{project['name']} - {project.get('state', 'N/A')}")
                item.setData(Qt.ItemDataRole.UserRole, project)
                self.projects_list.addItem(item)
        except Exception as e:
            print(f"Failed to load projects: {e}")
    
    def _view_team_issues_silently(self):
        """View team issues without showing success popup."""
        if not self.current_team or not self.linear_client:
            return
        
        try:
            issues = self.linear_client.get_team_issues(self.current_team['id'])
            self._display_issues(issues, f"Team: {self.current_team['name']}")
        except Exception as e:
            print(f"Failed to load team issues: {e}")
    
    def _view_project_issues_silently(self):
        """View project issues without showing success popup."""
        if not self.current_project or not self.linear_client:
            return
        
        try:
            issues = self.linear_client.get_project_issues(self.current_project['id'])
            self._display_issues(issues, f"Project: {self.current_project['name']}")
        except Exception as e:
            print(f"Failed to load project issues: {e}")
    
    def _load_my_issues_silently(self):
        """Load my issues without showing success popup."""
        if not self.linear_client:
            return
        
        try:
            issues = self.linear_client.get_my_issues()
            self.my_issues_list.clear()
            
            # Filter out done/completed issues
            filtered_issues = [
                issue for issue in issues 
                if issue.get('state', {}).get('type', '').lower() not in ['completed', 'canceled']
            ]
            
            for issue in filtered_issues:
                state_name = issue.get('state', {}).get('name', 'Unknown')
                team_key = issue.get('team', {}).get('key', 'N/A')
                item_text = f"[{team_key}] {issue['identifier']}: {issue['title']} [{state_name}]"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, issue)
                self.my_issues_list.addItem(item)
        except Exception as e:
            print(f"Failed to load my issues: {e}")
    
    def _on_width_changed(self, value: int):
        """Handle width slider change."""
        # Just update the display, actual save happens on apply
        pass
    
    def _on_transparency_changed(self, value: int):
        """Handle transparency slider change."""
        # Just update the display, actual save happens on apply
        pass
    
    def _apply_settings(self):
        """Apply and save appearance settings."""
        width = self.width_slider.value()
        transparency = self.transparency_slider.value()
        
        self.config.set("window.header_width", width)
        self.config.set("window.transparency", transparency)
        self.config.save()
        
        QMessageBox.information(
            self,
            "Settings Applied",
            "Settings saved! The changes will be applied to the header.\n\n"
            "The header will update immediately if it's currently visible."
        )
        
        # Notify sticky header to update (if we have a reference to it)
        if hasattr(self, 'on_settings_applied'):
            self.on_settings_applied()

