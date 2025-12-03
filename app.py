"""HF Space entrypoint that delegates to demo/app.py."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
DEMO = ROOT / "demo"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(DEMO) not in sys.path:
    sys.path.insert(0, str(DEMO))

# Importing demo will launch the Gradio interface (demo.launch() is called inside).
import demo.app  # noqa: F401,E402
