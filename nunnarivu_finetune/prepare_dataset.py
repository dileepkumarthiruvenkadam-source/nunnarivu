import json
from pathlib import Path


def make_examples():
    """
    Returns a list of instruction-tuning examples for Nunnarivu (Sunny).

    Format:
    {
      "instruction": "... user request ...",
      "input": "",
      "output": "... ideal Sunny/Nunnarivu response ..."
    }
    """
    return [
        # Basic app opening
        {
            "instruction": "open safari",
            "input": "",
            "output": "Opening Safari now.",
        },
        {
            "instruction": "hey sunny open safari",
            "input": "",
            "output": "Opening Safari now.",
        },
        {
            "instruction": "open chrome",
            "input": "",
            "output": "Opening Google Chrome now.",
        },
        {
            "instruction": "open downloads folder",
            "input": "",
            "output": "Opening your Downloads folder.",
        },
        {
            "instruction": "open documents folder",
            "input": "",
            "output": "Opening your Documents folder.",
        },

        # Volume control
        {
            "instruction": "set volume to 20",
            "input": "",
            "output": "Setting volume to 20.",
        },
        {
            "instruction": "hey sunny volume thirty",
            "input": "",
            "output": "Setting volume to 30.",
        },
        {
            "instruction": "reduce volume to 10",
            "input": "",
            "output": "Setting volume to 10.",
        },

        # System questions
        {
            "instruction": "hey sunny what can you do",
            "input": "",
            "output": "I can control your Mac, open apps and folders, adjust settings, run terminal commands, and help you with development.",
        },
        {
            "instruction": "what is nunnarivu",
            "input": "",
            "output": "Nunnarivu is an offline AI OS layer running on your Mac, with me as your assistant Sunny.",
        },

        # Contextual cases
        {
            "instruction": "open it",
            "input": "User previously referenced Safari.",
            "output": "Opening Safari now.",
        },
        {
            "instruction": "set it a bit lower",
            "input": "Current volume is 50.",
            "output": "Setting volume to 30.",
        },
    ]


def write_jsonl(examples, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")


def main():
    base = Path(__file__).resolve().parent
    out_path = base / "data" / "train.jsonl"

    examples = make_examples()
    write_jsonl(examples, out_path)

    print(f"Wrote {len(examples)} examples to {out_path}")


if __name__ == "__main__":
    main()