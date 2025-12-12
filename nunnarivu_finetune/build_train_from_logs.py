import json
import os
from pathlib import Path

# Where router.py is logging interactions
LOG_PATH = os.path.expanduser("~/nunnarivu/logs/nunnarivu_interactions.jsonl")

# Where we will write a training file
OUT_PATH = Path("nunnarivu_finetune/data/from_logs.jsonl")


def iter_logs(path: str):
    """Yield parsed JSON entries from the log file."""
    if not os.path.exists(path):
        print(f"[WARN] No log file found at {path}")
        return

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                print(f"[WARN] Skipping bad line: {line[:80]}...")
                continue


def build_dataset():
    os.makedirs(OUT_PATH.parent, exist_ok=True)
    n = 0

    with open(OUT_PATH, "w") as out_f:
        for entry in iter_logs(LOG_PATH):
            user_text = entry.get("user_text", "").strip()
            assistant_reply = entry.get("assistant_reply", "").strip()

            # Skip empty stuff
            if not user_text or not assistant_reply:
                continue

            sample = {
                "instruction": user_text,
                "input": "",
                "output": assistant_reply,
            }
            out_f.write(json.dumps(sample) + "\n")
            n += 1

    print(f"[OK] Wrote {n} samples to {OUT_PATH}")


if __name__ == "__main__":
    build_dataset()
