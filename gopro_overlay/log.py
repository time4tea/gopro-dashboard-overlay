import sys


def log(s):
    print(s, file=sys.stderr)

def fatal(s, error=True):
    log(s)
    exitcode = 1 if error else 0
    exit(exitcode)
