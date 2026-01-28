import ctypes
import sys
import subprocess

def is_admin():
    """Checks if the script is running with Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_command(command, shell=True):
    """Runs a system command and returns the output context."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=shell,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), -1

def elevate():
    """Re-launches the current process with administrative privileges."""
    if is_admin():
        return
    
    try:
        # Re-run the script with Admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            " ".join(sys.argv), 
            None, 
            1
        )
        sys.exit() # Exit the non-admin instance
    except Exception as e:
        print(f"Failed to elevate: {e}")
