"""Script to build the project using Nuitka.

This should be run by developers to create a standalone executable.
To run the project from source:

    python -m damasen

"""

import argparse
from itertools import cycle
from subprocess import Popen, PIPE
import sys
import time

parser = argparse.ArgumentParser()
args = parser.parse_args()
progress_bar = cycle(r"-\|/")
print("Building with Nuitka... /", end="")
command = [
    sys.executable,
    "-m",
    "nuitka",
    "--standalone",
    "--remove-output",
    "--disable-console",
    "--mingw64",
    "--lto=yes",
    "--python-flag=no_docstrings",
    "--assume-yes-for-downloads",
    "damasen",
]
process = Popen(command, shell=False, stdout=PIPE, stderr=PIPE, encoding="utf-8")
sys.stdout.flush()
while (code := process.poll()) is None:
    print(f"\b{next(progress_bar)}", end="")
    sys.stdout.flush()
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break

if code == 0:
    print("\bDone")
else:
    stdout, stderr = process.communicate()
    print("\bFAILURE")
    if stdout:
        print(stdout)
    if stderr:
        print(stderr)
