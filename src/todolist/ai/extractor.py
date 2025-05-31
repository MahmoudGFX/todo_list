"""
ChatGPT-powered TODO extractor – full implementation.

Swap the ENV-var OPENAI_API_KEY or pass api_key=… manually.
"""

from __future__ import annotations

import json
import os
from typing import List, Dict, Any

from openai import OpenAI

__all__ = ["GPTTodoExtractor"]

# --------------------------------------------------------------------------- #
# Prompt you asked me to use verbatim – tweak as you wish.                    #
# --------------------------------------------------------------------------- #
SYSTEM_MSG = (
    "Analyze the input text and extract a structured to-do list. "
    "Identify any sentences that imply future action or intent (e.g., "
    "“I'll check,” “I will do,” “I need to,” etc.). Return a JSON object "
    "with a list of tasks. Each task must include:\n"
    "* `description`: brief summary\n* `priority`: high|medium|low\n\n* `shot`: fhm_1620\n\n"
    "Output ONLY pure JSON."
)


class GPTTodoExtractor:
    """
    Wrapper around OpenAI chat completions.

    @param api_key: Explicit key; falls back to $OPENAI_API_KEY.
    @param model:   Model name (default 'gpt-4.1-mini').
    @param temperature: Sampling temperature.
    @param top_p:   top-p nucleus sampling.
    @param max_tokens:  Output token cap.
    @param store:   Persist the call on OpenAI’s side.
    """

    def __init__(
            self,
            api_key: str | None = None,
            model: str = "gpt-4.1-mini",
            temperature: float = 1.0,
            top_p: float = 1.0,
            max_tokens: int = 2048,
            store: bool = True,
    ) -> None:
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise RuntimeError("OPENAI_API_KEY missing; set env var or pass api_key.")
        self._model = model
        self._temperature = temperature
        self._top_p = top_p
        self._max_tokens = max_tokens
        self._store = store
        self._client = OpenAI(api_key=self._api_key)

    # --------------------------------------------------------------------- #
    # public                                                                #
    # --------------------------------------------------------------------- #
    def extract(self, raw_text: str) -> List[Dict[str, Any]]:
        """
        Talk to GPT and return structured tasks.

        @param raw_text: Unedited meeting/notes text.
        @return list[dict]: [{'description': str, 'priority': 'high'|…}, …]
        """
        if not raw_text.strip():
            return []

        # try:
        # print('raw_text')
        # print(raw_text)
        return self._call_openai(raw_text)
        # except Exception as exc:  # noqa: BLE001
        #     # Fallback so the UI doesn’t crash in demos.
        #     print(f"[GPTTodoExtractor] Warning – using stub due to: {exc}")
        #     return self._mock_response()

    # --------------------------------------------------------------------- #
    # internals                                                             #
    # --------------------------------------------------------------------- #
    def _call_openai(self, raw_text: str) -> List[Dict[str, Any]]:
        """
        OpenAI request + agnostic parsing for all current SDK shapes
        (responses.create / chat.completions / legacy).
        """
        resp = self._client.responses.create(
            model=self._model,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": SYSTEM_MSG}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": raw_text}],
                },
            ],
            text={"format": {"type": "text"}},
            reasoning={},
            tools=[],
            temperature=self._temperature,
            max_output_tokens=self._max_tokens,
            top_p=self._top_p,
            store=self._store,
        )

        # -------------------------- unwrap assistant text ---------------- #
        chunks: list[str] = []

        # 1) New /responses endpoint → resp.output[...].content[...].text
        if hasattr(resp, "output") and resp.output:
            for msg in resp.output:
                for part in getattr(msg, "content", []):
                    txt = getattr(part, "text", None)
                    if isinstance(txt, str):
                        chunks.append(txt)

        # 2) Fallback to resp.text.value (ResponseTextConfig)
        if not chunks and hasattr(resp, "text") and hasattr(resp.text, "value"):
            chunks.append(resp.text.value)

        # 3) Classic chat endpoint
        if not chunks and hasattr(resp, "choices"):
            chunks.append(resp.choices[0].message.content)           # type: ignore[attr-defined]

        if not chunks:
            raise ValueError(f"Unsupported OpenAI response: {type(resp)}")

        raw_out = "\n".join(chunks).strip()

        # -------------------------- strip ```json fences ------------------ #
        import re

        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_out,
                         flags=re.IGNORECASE | re.MULTILINE | re.DOTALL).strip()

        # -------------------------- JSON -> python ------------------------ #
        data = json.loads(cleaned)

        # Accept either {"tasks":[...]} or bare [...]
        return data["tasks"] if isinstance(data, dict) else data


if __name__ == "__main__":
    extractor = GPTTodoExtractor()  # relies on $OPENAI_API_KEY
    notes = (
        "good morning guys we are going to review the shots today , I think Mahmoud will send the final storyboard by EOD for shto jid_7982.\n"
        "We should book render farm time Thursday evening."
    )
    print(extractor.extract(notes))
    # ➜ [{'description': 'Send final storyboard to client', 'priority': 'high'}, …]
