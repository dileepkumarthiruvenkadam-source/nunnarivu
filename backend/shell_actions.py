import subprocess
from typing import Tuple


def run_shell_command(command: str, timeout: int = 10) -> Tuple[str, str, int]:
    """
    Run a shell command and return (stdout, stderr, exit_code).

    - command: the shell command as a single string, e.g. "ls -la"
    - timeout: max seconds to allow the command to run

    NOTE:
    - This runs in the user's environment, so it has the same permissions
      as your current user in the terminal.
    - Be careful with destructive commands like 'rm -rf'.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        return stdout, stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Command timed out after {timeout} seconds.", -1
    except Exception as e:
        return "", f"Error running command: {e}", -1


if __name__ == "__main__":
    # Quick manual test:
    out, err, code = run_shell_command("ls")
    print("exit code:", code)
    print("stdout:\n", out)
    print("stderr:\n", err)