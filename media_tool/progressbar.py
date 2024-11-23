"""
Progress bar class.
"""
import curses
import time


class ProgressBar:
    total_lines: int
    total_cols: int
    stdscr = None
    info_lines = []

    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        self.total_lines, self.total_cols = self.get_area_info()

    def get_area_info(self) -> tuple[int, int]:
        """Get the area info of the window."""
        total_lines, total_cols = self.stdscr.getmaxyx()
        return (total_lines, total_cols)

    def print_progress_bar(
        self,
        iteration: int,
        total: int,
        prefix: str = "",
        length: int = 50,
        fill: str = "█",
        suffix: str = "",
    ) -> None:
        """Print the progress bar."""

        self.stdscr.clear()

        percent = ("{0:.1f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + "-" * (length - filled_length)

        progress_str = f"{prefix} |{bar}| {percent}% Complete {suffix}"
        self.stdscr.addstr(0, 0, progress_str)

    def print_other_info(self, info: str = "") -> None:
        """Print other information."""

        self.info_lines.append(info)
        if len(self.info_lines) > self.total_lines - 3:
            self.info_lines.pop(0)  # Keep only the last (total_lines - 3) lines

        for i, line in enumerate(self.info_lines):
            self.stdscr.addstr(i + 2, 0, line)

    def before_exit(self) -> None:
        """Print other information and wait for user input before exiting."""

        self.print_other_info()
        self.print_other_info("Process complete! Press any key to exit.")

        self.refresh()
        self.stdscr.getch()

    def refresh(self) -> None:
        """Refresh the window."""

        self.stdscr.refresh()


def main(stdscr: curses.window) -> None:
    """Main function to test the ProgressBar class."""

    total_iterations = 100

    progress_obj = ProgressBar(stdscr)

    for i in range(total_iterations + 1):
        progress_obj.print_progress_bar(
            i, total_iterations, prefix="Progress:", length=50
        )
        progress_obj.print_other_info(
            f"Other information: Processing item {i}/{total_iterations}"
        )
        progress_obj.refresh()
        time.sleep(0.1)  # Simulate some work being done
    progress_obj.before_exit()


if __name__ == "__main__":
    curses.wrapper(main)
