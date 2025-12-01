# Linear Task Header

A PyQt6-based always-on-top sticky GUI application that displays Linear issues/tasks in a persistent header at the top of your screen. Stay focused on your current task with visual reminders and easy status updates.

## Features

- **Always-on-top sticky header**: Displays your current task at the top-middle of your screen (configurable size)
- **Linear API integration**: Browse teams, projects, and issues directly from the app
- **Hotkey support**: Toggle navigation window with a configurable hotkey (default: Ctrl+W)
- **Status management**: Update issue status directly from the sticky header
- **Custom tasks**: Create local tasks that aren't in Linear
- **Markdown generation**: Export issues to markdown files with checkboxes
- **Bidirectional sync**: Edit checkboxes in markdown and sync changes back to Linear
- **Large, readable font**: 40px font by default for easy visibility

## Installation

### Prerequisites

- Python 3.8 or higher
- Linear account with API access

### Setup

1. Clone this repository:

```bash
git clone <repository-url>
cd task-header
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Get your Linear API key:
   - Go to <https://linear.app/settings/api>
   - Create a new Personal API Key
   - Copy the key

4. Run the application:

```bash
python main.py
```

5. On first run:
   - The navigation window will open
   - Enter your Linear API key and click "Save API Key"
   - Browse your teams/projects/issues

## Usage

### Setting an Active Issue

1. Press the hotkey (default: **Ctrl+W**) to open the navigation window
2. Navigate through tabs:
   - **Teams**: View all your teams
   - **Projects**: View projects for a selected team
   - **Issues**: View issues for a team or project
   - **My Issues**: View all issues assigned to you
   - **Custom Task**: Create a custom task

3. Select an issue and click "Set as Active Issue"
4. The sticky header will appear at the top of your screen displaying the issue

### Updating Issue Status

- In the sticky header, use the status dropdown to change the issue state
- Changes sync immediately to Linear

### Creating Custom Tasks

1. Go to the "Custom Task" tab
2. Enter your task description
3. Click "Set as Active Task"
4. The task will appear in the sticky header

### Generating Markdown Files

1. Navigate to the "My Issues" tab
2. Click "Refresh My Issues"
3. Click "Generate my-issues.md"
4. A markdown file will be created with all your issues as checkboxes

#### Markdown Format

Generated markdown files use this format:

```markdown
# My Issues

*Generated: 2025-12-01 12:00:00*

## Started

- [ ] **ABC-123**: Implement user authentication *[In Progress]* <!-- id:issue_id_here -->
- [ ] **ABC-124**: Fix navigation bug *[Started]* <!-- id:issue_id_here -->

## Completed

- [x] **ABC-122**: Setup project *[Done]* <!-- id:issue_id_here -->
```

#### Syncing Markdown Changes to Linear

When you check/uncheck boxes in the markdown file, the changes can be synced back to Linear:

1. Edit the markdown file and check/uncheck boxes
2. Save the file
3. If auto-sync is enabled (default), changes will automatically sync to Linear
4. Issues will be moved to "Completed" or reopened based on checkbox state

### Hotkey Configuration

To change the hotkey:

1. Open the config file: `~/.linear_task_header_config.json`
2. Change the `hotkey` value (e.g., "ctrl+shift+l", "alt+l")
3. Restart the application

Supported modifiers: `ctrl`, `shift`, `alt`, `meta`

### Window Configuration

The sticky header can be customized by editing the config file:

```json
{
  "window": {
    "width_percent": 10,
    "height_percent": 10,
    "position": "top-middle"
  },
  "font_size": 40
}
```

## Configuration

The application stores configuration in `~/.linear_task_header_config.json`:

- **linear_api_key**: Your Linear API key
- **hotkey**: Global hotkey to toggle navigation (default: "ctrl+w")
- **current_issue_id**: Currently displayed issue
- **font_size**: Font size for issue display (default: 40)
- **window**: Window size and position settings
- **markdown**: Markdown generation and sync settings

## Troubleshooting

### Hotkey not working

- Make sure no other application is using the same hotkey
- Try a different hotkey combination
- On some systems, you may need to run the application with administrator/elevated privileges

### API key not working

- Verify your API key is correct
- Check that your Linear account has API access
- Make sure you have internet connectivity

### Sticky header not appearing

- Check that an issue is selected
- Verify the window isn't positioned off-screen
- Try deleting the config file and reconfiguring

### Markdown sync not working

- Ensure the markdown file has the correct format with `<!-- id:issue_id -->` comments
- Check that auto-sync is enabled in settings
- Verify your Linear API key has write permissions

## Architecture

- **main.py**: Application entry point and coordinator
- **config.py**: Configuration management
- **linear_client.py**: Linear API client using GraphQL
- **sticky_header.py**: Always-on-top issue display widget
- **navigation_window.py**: Main navigation interface
- **markdown_sync.py**: Markdown generation and synchronization

## Requirements

See `requirements.txt`:

- PyQt6: GUI framework
- requests: HTTP requests for Linear API
- python-dotenv: Environment variable management
- keyboard: Global hotkey handling
- watchdog: File system monitoring for markdown sync
