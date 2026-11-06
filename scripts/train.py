import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.ml.pipeline import train

if __name__ == "__main__":
    print("Trained category and sentiment models:", train()["version"])
