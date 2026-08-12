#!/usr/bin/env python3

from torbot.cli import get_version, main, run, set_arguments

__all__ = ["get_version", "main", "run", "set_arguments"]


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupt received! Exiting cleanly...")
