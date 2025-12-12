# Nunnarivu — Sunny (Local macOS Assistant)

Nunnarivu (a.k.a. Sunny) is a local macOS assistant focused on developer productivity.
It provides both a text-based coding assistant and an offline-capable voice interface.

This repository contains the voice listener, routing and action execution logic,
an LLM client interface (to a self-hosted Ollama model), CLI entrypoints, and
helper modules for macOS automation and TTS.

**Quick highlights:**
- **Voice:** Wake-word + Vosk offline recognition (`models/vosk-model-small-en-us-0.15`).
- **Router:** Fast-path commands (e.g. `open <app>`) plus LLM-driven JSON action protocol.
- **LLM:** `backend/llm_client.py` posts prompts to a local Ollama server.
- **Privacy:** Router masks long digit sequences and skips logging for very sensitive keywords.

**Contents**
- `sunny_dev.py` — interactive LLM chat assistant (developer mode).
- `sunny_voice.py` — voice entrypoint (wake word + conversation).
- `cli/nunnarivu_terminal.py` — simple terminal UI for text input.
- `backend/` — core modules: `router.py`, `llm_client.py`, `voice_listener.py`, helpers.
- `models/` — offline speech models (Vosk).
- `tests/` — unit tests (router logging/privacy, app-opening behavior, etc.).

**Requirements**
Dependencies are listed in `requirements.txt`. Important packages include:
- `vosk`, `sounddevice` (voice input)
- `requests` (LLM HTTP client)
- `python-docx`, `beautifulsoup4` (cover letter generation)

Recommended: create a virtual environment before installing.

Installation
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Quick start

- Interactive coding assistant (text):
```
python sunny_dev.py
```

- Terminal client (text routing):
```
python cli/nunnarivu_terminal.py
```

- Voice assistant (requires microphone + Vosk model):
```
python sunny_voice.py
```

Notes and configuration
- LLM: `backend/llm_client.py` currently targets an Ollama HTTP endpoint. Update
	`OLLAMA_URL` and `MODEL_NAME` if your server is at a different address.
- Vosk model: the project includes `models/vosk-model-small-en-us-0.15/`. Keep that
	folder in place or update `backend/voice_listener.py` to point to the correct model path.
- Logging: interactions are written to `~/nunnarivu/logs/nunnarivu_interactions.jsonl`.
	The router masks long digit sequences and will skip logging for some sensitive keywords.
- macOS actions: `backend/mac_actions.py` contains helpers that use macOS tools — these
	expect a macOS environment.

Testing
```
pip install pytest
pytest -q
```

Notes for contributors
- Keep the JSON action protocol in `backend/router.py` stable. The router expects the
	model to return a single JSON object with `action`, `args`, and `assistant_reply`.
- If adding new actions, update the router and corresponding helpers under `backend/`.

Further work / TODO
- Add a `backend/server.py` HTTP wrapper (file exists but is currently empty).
- Improve `README.md` with architecture diagram and examples (PRs welcome).

If you need a different layout or more details (examples, screenshots, CI), tell me
what you'd like and I will update the README accordingly.

