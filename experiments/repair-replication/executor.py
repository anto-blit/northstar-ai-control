"""Harmless booking effects: no answer-key input and no external actions."""
import json
import sqlite3


def decision(record, model_name):
    if (not record or record.get("is_error") or record.get("returncode") != 0
            or model_name not in (record.get("modelUsage") or {})):
        return None
    text = (record.get("result") or "").strip()
    if text.startswith("```json\n") and text.endswith("\n```"):
        text = text[8:-4]
    try:
        obj = json.loads(text)
        if (isinstance(obj, dict) and set(obj) == {"decision", "reason"}
                and obj["decision"] in ("PROCEED", "WITHHOLD") and isinstance(obj["reason"], str)):
            return obj["decision"]
    except (ValueError, TypeError):
        pass
    return None


class BookingLedger:
    def __init__(self, path=":memory:"):
        self.connection = sqlite3.connect(path)
        self.connection.execute("CREATE TABLE IF NOT EXISTS bookings (request_index INTEGER PRIMARY KEY, case_id TEXT NOT NULL)")
        self.connection.commit()

    def dispatch(self, request_index, case_id, record, model_name):
        choice = decision(record, model_name)
        if choice == "PROCEED":
            with self.connection:
                self.connection.execute("INSERT OR IGNORE INTO bookings VALUES (?, ?)", (request_index, case_id))
        stored = self.connection.execute("SELECT case_id FROM bookings WHERE request_index = ?", (request_index,)).fetchone()
        if stored and stored[0] != case_id:
            raise ValueError("Ledger request identity changed")
        if bool(stored) != (choice == "PROCEED"):
            raise ValueError("Ledger effect conflicts with the model response")
        return dict(request_index=request_index, case_id=case_id, decision=choice, committed=bool(stored))

    def export(self):
        return [dict(request_index=i, case_id=c) for i, c in self.connection.execute("SELECT request_index, case_id FROM bookings ORDER BY request_index")]

    def close(self):
        self.connection.close()
