```markdown
# Todo-AI  
Lightweight desktop (or Maya-embedded) assistant that turns raw meeting notes—**typed *or spoken***—into a live, timestamped to-do list using OpenAI + PySide 6.

---

## Features
* **GPT extraction** – paste text *or dictate* notes; AI returns structured tasks with inferred priority.  
* **Voice input ready** – optional microphone capture pipes straight into the extractor (see *Voice input* below).  
* **JSON persistence** – `todos.json` acts like a tiny DB (never deletes, only appends).  
* **Live GUI** – sortable table, double-click ✓ to mark complete.  
* **Background watcher** – stamps `start_time` the first hour a task exists.  
* **Clean package split** – `ai / core / gui` modules for easy reuse in Maya, Houdini, etc.  
* **Mobile companion (coming soon)** – a phone plug-in is under review; once published you’ll be able to dictate meetings on the go and sync to the desktop JSON.

---

## Folder layout
```

todo\_list/
└─ src/
├─ ai/          # GPT wrapper
├─ core/        # dataclass, JSON I/O, watcher
├─ gui/         # PySide6 widgets & window
└─ main.py      # entry-point

````

---

## Quick start

1. **Install deps**

   ```bash
   pip install openai PySide6
````

*Voice capture (optional):*

```bash
pip install SpeechRecognition pyaudio
```

2. **Set your key**

   ```bash
   export OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXX
   ```

3. **Run**

   ```bash
   python todo_list/src/main.py
   ```

4. **Demo notes**

   ```
   Mahmoud will send the final storyboard today.
   We need to book extra render farm time for Thursday evening.
   ```

   Click **Extract ➜ Append** – tasks instantly appear in the table and in *todos.json*.

---

## Voice input (optional)

1. Plug in a mic.
2. Inside the GUI press **Voice Record** (button exposed when the `SpeechRecognition` lib is present).
3. Speak your notes → the transcript is fed to GPT like normal text.

*(No mic? Just keep pasting text.)*

---

## Inside Maya (optional)

```python
import sys, pathlib
sys.path.append(r"D:\GitHub\femtotools\todo_list\src")
from main import main
main()          # launches the same PySide6 window inside Maya 2023+
```

---

## Configuration

| Variable / Arg      | Purpose                                                                                | Default |
| ------------------- | -------------------------------------------------------------------------------------- | ------- |
| `OPENAI_API_KEY`    | Secret key for OpenAI API                                                              | *none*  |
| `--TODO_DEBUG` flag | If passed (`python ... TODO_DEBUG`) sets watcher interval to **10 s** for fast testing | 3600 s  |

---

## Extending

* **Storage** – swap `core/storage.py` for SQLite or ShotGrid calls.
* **Watcher** – add Slack / email pings on overdue items.
* **Phone plug-in** – REST hooks will sync remote dictations into `todos.json` once the app is live.
* **GUI** – filter, sort by priority, drag-drop re-ordering, etc.

---

## License

MIT – do whatever you want, but don’t blame me if it breaks 😊


