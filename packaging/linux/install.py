"""Run the bundled user installer with isolated Python imports."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))

if __name__ == "__main__":
    from shiwen.install import main

    main()
