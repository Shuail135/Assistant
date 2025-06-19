import subprocess
import sys
import os

def run_gui_standalone():
    subprocess.Popen([
        sys.executable,
        "-m", "settings.setting_GUI"
    ], cwd=os.path.dirname(__file__))


def run(request_input):
    run_gui_standalone()
    return "Opening Settings..."
