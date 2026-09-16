"""Use the packaged Python modules and the distribution's GTK/WebKit bindings."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))

if __name__ == "__main__":
    from shiwen.app import main

    main()
