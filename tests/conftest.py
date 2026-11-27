import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
for p in ["tools/hooks", ".kiro/skills/spec-gate/scripts", ".kiro/skills/touch-index/scripts"]:
    sys.path.insert(0, str(ROOT / p))
