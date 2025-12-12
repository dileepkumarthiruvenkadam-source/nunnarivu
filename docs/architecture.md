# Nunnarivu — System Architecture (Version 0.1)
_Last updated: December 2025_

---

# 1. Overview

Nunnarivu is an **AI OS Layer for macOS**.  
It converts **natural language → real macOS actions** with:

- No hardcoding  
- Full automation  
- Works on ANY Mac  
- Self-learning by logging interactions  
- Local LLM (phi3-mini via Ollama)  
- Dynamic app discovery  
- Expandable action system  

---

# 2. High-Level Architecture

```
User
 ↓
cli/nunnarivu_terminal.py
 ↓
router.py  ← Central Brain
 ↓
LLM (phi3 via Ollama)
 ↓
JSON Action
 ↓
Action Executors
 ↓
macOS (Apps, Folders, Shell, Docs)
```

---

# 3. Module Breakdown

---

## 3.1 `backend/llm_client.py`

Handles communication with Ollama:

- Sends system prompt + user message  
- Enforces streaming OFF  
- Ensures JSON-only responses  
- Handles timeouts/errors  
- Returns *raw* model output  

---

## 3.2 `backend/router.py` — **THE MAIN BRAIN**

Responsibilities:

1. Build the system prompt  
2. Ask LLM for JSON  
3. Parse JSON safely  
4. Execute real macOS actions  
5. Log every interaction  
6. Return assistant reply  

### Valid Actions

| Action | JSON Example | Purpose |
|--------|--------------|---------|
| `open_app` | `{"name": "Safari"}` | open applications |
| `set_volume` | `{"level": 50}` | set system volume |
| `open_folder` | `{"path": "~/Downloads"}` | open Finder folder |
| `run_shell` | `{"command": "ls -la"}` | execute shell |
| `create_cover_letter` | `{"url": "...", "name": "Applicant"}` | generate docx |
| `none` | `{}` | normal chat |

---

### JSON Parsing Rules

Router uses `_parse_action_json(raw)`:

- direct `json.loads`  
- OR extract first `{...}` block automatically  
- fallback: plain text reply  

---

### Interaction Logging

Every request is saved automatically:

File:
```
~/nunnarivu/logs/nunnarivu_interactions.jsonl
```

Format:
```json
{
  "timestamp": 1764971152.4,
  "user_text": "open chrome",
  "assistant_action": {"action": "open_app", "args": {"name": "google chrome"}},
  "assistant_reply": "Opening Google Chrome."
}
```

Used later for fine-tuning.

---

## 3.3 `backend/discover_apps.py` — UNIVERSAL APP DISCOVERY

Zero hardcoding.

It scans:

- `/Applications`
- `~/Applications`

Creates:

```
backend/app_index.json
```

Example:
```json
{
  "google chrome": "/Applications/Google Chrome.app",
  "visual studio code": "/Applications/Visual Studio Code.app",
  "facetime": "/Applications/FaceTime.app",
  "spotify": "/Applications/Spotify.app"
}
```

Works on ANY Mac in the world.

---

## 3.4 `backend/app_matcher.py` — SMART APP MATCHING

Features:

### ✓ Normalization  
- remove `.app`  
- lower-case  
- remove punctuation  
- replace symbols  
- alias generation  
- multi-word reduction  

### ✓ Fuzzy Matching  
User: “open studio” → matches “Visual Studio Code”

### ✓ Multi-Match Disambiguation  
User: “open microsoft”

Sunny:  
```
I found multiple apps matching 'microsoft':
- Microsoft Word
- Microsoft Excel
- Microsoft Outlook
Say: "open Microsoft Word"
```

### ✓ Full Automation  
No manual alias list.  
Aliases are built from app names at runtime.

---

## 3.5 `backend/mac_actions.py`

Handles:

### 👉 Open apps  
Find correct path → launch via `open "path"`.

### 👉 Open folders  
`open ~/Downloads`

### 👉 Set volume  
Using AppleScript.

### 👉 (Future) Close app  
### 👉 (Future) Kill app  
### 👉 (Future) Open last file from app  
### 👉 (Future) Open windows/settings panels  

---

## 3.6 `backend/shell_actions.py`

Executes UNIX commands safely:

- returns stdout  
- stderr  
- exit code  

Example output:

```
exit code: 0
stdout:
 backend
 cli
 models

stderr:
 (empty)
```

---

## 3.7 `backend/cover_letter.py`

Input: job posting URL  
Output: DOCX file generated in `~/Nunnarivu/Generated/`.

Steps:

1. Scrape webpage  
2. Extract job text  
3. Send to LLM to write cover letter  
4. Save DOCX  
5. Return file path  

---

## 3.8 Training Data Builder  
`nunnarivu_finetune/build_train_from_logs.py`

Converts logs → training dataset.

Example final training JSONL:

```json
{"instruction": "open safari", "input": "", "output": "Opening Safari."}
{"instruction": "hey", "input": "", "output": "Hello! How can I assist you today?"}
{"instruction": "open image", "input": "", "output": "I found Image Capture, Image Playground…"}
```

This lets Nunnarivu **self-improve**.

---

# 4. Runtime Flow (Step-by-Step)

```
User: "open chrome"
↓
router.py builds system prompt
↓
LLM returns JSON:
{
  "action": "open_app",
  "args": {"name": "chrome"},
  "assistant_reply": "Opening Google Chrome."
}
↓
router loads app_index.json
↓
app_matcher finds Google Chrome
↓
mac_actions opens correct path
↓
router logs everything
↓
Reply shown to user
```

---

# 5. Example Commands & Behavior

| User Says | Sunny Does |
|-----------|------------|
| open chrome | opens Google Chrome |
| open studio | opens Visual Studio Code |
| open microsoft | asks which one |
| open image | asks Image Capture or Image Playground |
| open face | opens FaceTime |
| open safari | opens Safari |
| hey | replies normally |
| create cover letter for this URL | generates DOCX |
| run ls -la | terminal command |

---

# 6. Why This Architecture Works

✓ Universal — works on any Mac  
✓ Modular — easy to extend  
✓ Fully automated — no hardcoding  
✓ LLM-controlled behavior  
✓ Self-learning — improves over time  
✓ Fast — <0.2 sec for matched apps  
✓ Human-safe — router controls actions  

---

# 7. Future Expansions

### 🔧 Local Model (Nunnarivu Local)
Specialized LLM for:
- app mappings  
- macOS control  
- fuzzy actions  
- safety rules  

### ☁️ Server Model (Nunnarivu Server)
Big model for:
- reasoning  
- document generation  
- planning  
- external API tasks  

### 📦 New Features
- window management  
- screenshots & screen reading  
- model auto-finetuning every week  
- plugin system  
- workflow automation  

---

# 8. Directory Structure (Current)

```
nunnarivu/
 ├── backend/
 │    ├── router.py
 │    ├── llm_client.py
 │    ├── mac_actions.py
 │    ├── shell_actions.py
 │    ├── discover_apps.py
 │    ├── app_matcher.py
 │    ├── cover_letter.py
 │    └── app_index.json (auto-generated)
 │
 ├── cli/
 │    └── nunnarivu_terminal.py
 │
 ├── logs/
 │    └── nunnarivu_interactions.jsonl
 │
 ├── nunnarivu_finetune/
 │    ├── build_train_from_logs.py
 │    └── data/
 │
 ├── venv/
 ├── roadmap.txt
 └── README.md
```

---

# END OF DOCUMENT