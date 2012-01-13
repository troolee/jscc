import sys
from manager import Manager


def main():
    run(sys.argv)


def run(argv):
    Manager().run(argv)
