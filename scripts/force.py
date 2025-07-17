import curses
import os
import subprocess
import sys

ASSISTANTS = [
    "claude_code", "copilot", "continue", "cursor", "replit", "lovable"
]

CONFIG_FOLDERS = [
    ".force", ".copilot", ".continue", ".cursor", ".replit", ".lovable"
]

# --- TUI Windows ---
def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    menu_win = curses.newwin(height//2, width//2, 0, 0)
    config_win = curses.newwin(height//2, width//2, 0, width//2)
    status_win = curses.newwin(height//2, width, height//2, 0)

    menu_win.box()
    config_win.box()
    status_win.box()

    menu_win.addstr(1, 2, "FORCE Project TUI")
    menu_win.addstr(3, 2, "1. Initialize Force Project")
    menu_win.addstr(4, 2, "2. Import Components")
    menu_win.addstr(5, 2, "3. Choose Coding Assistant")
    menu_win.addstr(6, 2, "Q. Quit")
    menu_win.refresh()

    config_win.addstr(1, 2, "Config Options:")
    for idx, assistant in enumerate(ASSISTANTS):
        config_win.addstr(3+idx, 4, f"{idx+1}. {assistant}")
    config_win.refresh()

    status_win.addstr(1, 2, "Status Log:")
    status_win.refresh()

    while True:
        key = stdscr.getch()
        if key in [ord('q'), ord('Q')]:
            break
        elif key == ord('1'):
            status_win.addstr(3, 2, "Initializing Force Project...")
            status_win.refresh()
            initialize_force_project()
        elif key == ord('2'):
            status_win.addstr(4, 2, "Importing Components...")
            status_win.refresh()
            import_components()
        elif key == ord('3'):
            status_win.addstr(5, 2, "Choose Coding Assistant...")
            status_win.refresh()
            choose_assistant(config_win, status_win)

# --- Logic ---
def initialize_force_project():
    for folder in CONFIG_FOLDERS:
        if not os.path.exists(folder):
            os.makedirs(folder)

def import_components():
    # Placeholder: implement batch import logic
    pass

def choose_assistant(config_win, status_win):
    config_win.addstr(10, 2, "Select assistant by number:")
    config_win.refresh()
    curses.echo()
    choice = config_win.getstr(11, 2, 10).decode()
    curses.noecho()
    try:
        idx = int(choice) - 1
        assistant = ASSISTANTS[idx]
        status_win.addstr(7, 2, f"Selected: {assistant}")
        status_win.refresh()
        # Initialize hidden folder for assistant
        folder = f".{assistant}"
        if not os.path.exists(folder):
            os.makedirs(folder)
    except Exception:
        status_win.addstr(8, 2, "Invalid selection.")
        status_win.refresh()

# --- Git Tasks ---
def git_tag_and_branch():
    # Increment semantic version (placeholder logic)
    version = "v0.4.2"
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"chore: release {version}"])
    subprocess.run(["git", "tag", version])
    subprocess.run(["git", "tag", "release"])
    subprocess.run(["git", "checkout", "-b", f"release/{version}"])

if __name__ == "__main__":
    curses.wrapper(main)
    git_tag_and_branch()
