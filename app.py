"""HF Space entrypoint that delegates to demo/app.py."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
DEMO = ROOT / "demo"
SRC = ROOT / "src"
for path in (ROOT, DEMO, SRC):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

# Importing demo will launch the Gradio interface (demo.launch() is called inside).
import demo.app  # noqa: F401,E402
