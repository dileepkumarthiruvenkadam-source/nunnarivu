import subprocess


def run_osascript(script: str) -> None:
    """Run a small AppleScript snippet via osascript."""
    subprocess.run(
        ["osascript", "-e", script],
        check=False
    )


def open_app(app_name: str) -> None:
    """
    Open an app by name as shown in /Applications.

    Example:
      open_app("Safari")
    """
    script = f'tell application "{app_name}" to activate'
    run_osascript(script)


def close_app(app_name: str) -> None:
    """
    Close an app by name.

    Example:
      close_app("Safari")
    """
    script = f'tell application "{app_name}" to quit'
    run_osascript(script)


def open_url(url: str) -> None:
    """
    Open a URL in Safari.

    Example:
      open_url("https://google.com")
    """
    script = f'''
    tell application "Safari"
        activate
        open location "{url}"
    end tell
    '''
    run_osascript(script)


def open_folder(path: str) -> None:
    """
    Open a folder in Finder using a POSIX path.

    Example:
      open_folder("/Users/you/Downloads")
    """
    script = f'''
    tell application "Finder"
        activate
        open POSIX file "{path}"
    end tell
    '''
    run_osascript(script)


def set_volume(level: int) -> None:
    """
    Set system output volume (0–100).

    Example:
      set_volume(30)
    """
    level = max(0, min(level, 100))
    script = f"set volume output volume {level}"
    run_osascript(script)


if __name__ == "__main__":
    # manual test (uncomment to try):
    # open_app("Safari")
    # close_app("Safari")
    # open_url("https://google.com")
    # open_folder("/Users/YOURNAME/Downloads")
    # set_volume(20)
    pass