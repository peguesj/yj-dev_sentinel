import argparse
import curses
import os
import sys
from pathlib import Path
# from integration.fast_agent.force_mcp_server import main as force
class ForceTUI:
    def __init__(self, stdscr, debug=False):
        self.stdscr = stdscr
        self.debug = debug
        self.log_lines = []

        curses.curs_set(0)  # Hide cursor
        self.init_colors()
        self.stdscr.clear()

        self.load_ascii_art()
        self.show_splash_screen()

        self.init_options()  # load JSON option files
        self.questions = [
            {
                "question": "What is your favorite coding assistant?",
                "options": [x["name"] for x in self.options["ide"]],
                "context": "This helps determine which Force variant to select."
            },
            {
                "question": "What do you prioritize?",
                "options": ["Documentation", "Code Quality", "TDD", "Rapid Prototyping", "Vibe Coding"],
                "context": "This helps determine the focus areas for the agentic workflow."
            },
            {
                "question": "Are there any standards or frameworks you are beholden to?",
                "options": ["None", "PEP8", "Google Style", "Custom Lint", "Agile/Scrum"],
                "context": "This helps set constraints and guidelines for the workflow."
            },
            {
                "question": "Ready to initialize your Force environment?",
                "options": ["Yes", "No"],
                "context": "Confirm and start environment setup."
            },
        ]

        self.current_question = 0
        self.current_option = 0
        self.answers = []

        self.windows_initialized = False
        self.show_logs = False

    def log(self, message: str):
        if self.debug:
            self.log_lines.append(message)
            if len(self.log_lines) > 1000:
                self.log_lines.pop(0)

    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)   # header/footer
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW) # option highlight
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)   # question

    def load_ascii_art(self):
        ascii_art_path = os.path.join("docs", "assets", "force-ascii.txt")
        try:
            with open(ascii_art_path, "r", encoding="utf-8") as f:
                self.ascii_art_lines = f.readlines()
        except Exception as e:
            self.ascii_art_lines = ["(Failed to load ASCII art)"]
            self.log(f"Error loading ascii art: {e}")

    def show_splash_screen(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        pad_x = width // 10
        pad_y = height // 10

        max_art_width = width - 2 * pad_x
        max_art_height = height - 2 * pad_y

        art_to_display = self.ascii_art_lines[:max_art_height]
        art_to_display = [line[:max_art_width] for line in art_to_display]

        start_y = pad_y
        for i, line in enumerate(art_to_display):
            try:
                self.stdscr.addstr(start_y + i, pad_x, line, curses.A_DIM)
            except curses.error:
                pass

        prompt = "Press Enter to continue..."
        try:
            self.stdscr.addstr(height - pad_y - 1,
                               width // 2 - len(prompt) // 2,
                               prompt,
                               curses.A_BOLD | curses.A_REVERSE)
        except curses.error:
            pass

        self.stdscr.refresh()

        while True:
            k = self.stdscr.getch()
            if k in [curses.KEY_ENTER, ord('\n'), ord('\r')]:
                self.log("Splash screen: Enter pressed")
                break

    def init_windows(self):
        height, width = self.stdscr.getmaxyx()
        top_height = height // 2
        bottom_height = height - top_height

        self.top_win = curses.newwin(top_height, width, 0, 0)

        bottom_width = width // 2
        self.bottom_left_win = curses.newwin(bottom_height, bottom_width, top_height, 0)
        self.bottom_right_win = curses.newwin(bottom_height, width - bottom_width, top_height, bottom_width)

        self.top_win.bkgd(' ', curses.color_pair(3))

        self.windows_initialized = True
        self.log("Windows initialized")

    def draw_top(self):
        if not self.windows_initialized:
            return
        self.top_win.clear()
        question_info = self.questions[self.current_question]

        header_text = f"Force Environment Initialization (question {self.current_question + 1}/{len(self.questions)})"
        self.top_win.addstr(0, 0, header_text, curses.A_BOLD)

        self.top_win.addstr(2, 0, question_info["question"])

        self.top_win.refresh()

    def draw_bottom_left(self):
        if not self.windows_initialized:
            return
        self.bottom_left_win.clear()
        options = self.questions[self.current_question]["options"]

        max_width = self.bottom_left_win.getmaxyx()[1] - 1
        max_height = self.bottom_left_win.getmaxyx()[0]

        visible_options = options[:max_height] if len(options) > max_height else options

        for idx, option in enumerate(visible_options):
            display_option = option[:max_width]
            if idx == self.current_option:
                self.bottom_left_win.attron(curses.color_pair(2))
                self.bottom_left_win.addstr(idx, 0, display_option)
                self.bottom_left_win.attroff(curses.color_pair(2))
            else:
                self.bottom_left_win.addstr(idx, 0, display_option)
        self.bottom_left_win.refresh()

    def draw_bottom_right(self):
        if not self.windows_initialized:
            return
        self.bottom_right_win.clear()
        context = self.questions[self.current_question]["context"]
        self.bottom_right_win.addstr(0, 0, "Contextual Help:")
        self.bottom_right_win.addstr(2, 0, context)
        self.bottom_right_win.refresh()

    def draw_all(self):
        self.log("Drawing all UI components")
        self.draw_top()
        self.draw_bottom_left()
        self.draw_bottom_right()

    def run(self):
        self.log("Starting main run loop")
        self.init_windows()
        self.draw_all()

        while True:
            key = self.stdscr.getch()
            self.log(f"Key pressed: {key}")

            if key == ord('q'):
                self.log("Quitting due to 'q' key")
                break
            elif key == ord('l') and self.debug:
                self.show_logs = not self.show_logs
                self.log(f"Toggling logs display: {self.show_logs}")
                if self.show_logs:
                    self.display_logs()
                else:
                    self.draw_all()
            elif key == curses.KEY_DOWN or key == ord('j'):
                options_len = len(self.questions[self.current_question]["options"])
                if self.current_option < options_len - 1:
                    self.current_option += 1
                    self.log(f"Current option incremented: {self.current_option}")
                    self.draw_bottom_left()
            elif key == curses.KEY_UP or key == ord('k'):
                if self.current_option > 0:
                    self.current_option -= 1
                    self.log(f"Current option decremented: {self.current_option}")
                    self.draw_bottom_left()
            elif key == ord('\n') or key == curses.KEY_ENTER:
                answer = self.questions[self.current_question]["options"][self.current_option]
                self.answers.append(answer)
                self.log(f"Answer given for question {self.current_question}: {answer}")

                if self.current_question == len(self.questions) - 1:
                    self.display_summary()
                    break

                self.current_question += 1
                self.current_option = 0
                self.draw_all()

    def display_logs(self):
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "Debug Logs (press 'l' to return)", curses.A_BOLD)

        max_y, max_x = self.stdscr.getmaxyx()
        for i, line in enumerate(self.log_lines[-(max_y-2):]):
            try:
                self.stdscr.addstr(i+2, 0, line[:max_x-1])
            except curses.error:
                pass
        self.stdscr.refresh()
        while True:
            k = self.stdscr.getch()
            if k == ord('l'):
                break
    def show_splash_screen(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        pad_x = width // 10
        pad_y = height // 10

        max_art_width = width - 2 * pad_x
        max_art_height = height - 2 * pad_y

        art_to_display = self.ascii_art_lines[:max_art_height]
        art_to_display = [line[:max_art_width] for line in art_to_display]

        start_y = pad_y
        for i, line in enumerate(art_to_display):
            try:
                self.stdscr.addstr(start_y + i, pad_x, line, curses.A_DIM)
            except curses.error:
                pass

        # Hardcoded overlay texts & positions relative to height & width
        overlays = [
            (int(height * 0.40), width // 2, "FORCE"),
            (int(height * 0.55), int(width * 0.55), "engine"),
            (int(height * 0.70), width // 2, "Powered by Dev Sentinel and Fast Agent"),
            (int(height * 0.80), width // 2, "v.0.4.3"),
        ]

        for y, x_center, text in overlays:
            x_start = x_center - len(text) // 2
            if 0 <= y < height and 0 <= x_start < width:
                try:
                    self.stdscr.addstr(y, x_start, text, curses.A_BOLD | curses.A_STANDOUT)
                except curses.error:
                    pass

        prompt = "Press Enter to continue..."
        try:
            self.stdscr.addstr(height - pad_y - 1,
                               width // 2 - len(prompt) // 2,
                               prompt,
                               curses.A_BOLD | curses.A_REVERSE)
        except curses.error:
            pass

        self.stdscr.refresh()

        while True:
            k = self.stdscr.getch()
            if k in [curses.KEY_ENTER, ord('\n'), ord('\r')]:
                self.log("Splash screen: Enter pressed")
                break

    def display_summary(self):
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "Thank you! You have completed the configuration.", curses.A_BOLD)
        for idx, (q, a) in enumerate(zip([q["question"] for q in self.questions], self.answers)):
            line = f"{idx + 1}. {q} -> {a}"
            self.stdscr.addstr(idx + 2, 0, line)
        self.stdscr.addstr(len(self.questions) + 4, 0, "Press any key to exit.")
        self.stdscr.refresh()
        self.stdscr.getch()

def main():
    parser = argparse.ArgumentParser(description="Force environment TUI")
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    curses.wrapper(lambda stdscr: run_force_tui(stdscr, args.debug))

def run_force_tui(stdscr, debug=False):
    app = ForceTUI(stdscr, debug=debug)
    app.run()

if __name__ == '__main__':
    main()