#!/usr/bin/env python3
"""
EU5 Strategy Agent - Standalone Edition

Simple entry point for running the EU5 Strategy Advisor.
"""

import sys
from eu5_agent.cli import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
