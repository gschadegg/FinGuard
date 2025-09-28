import base64
import json
from datetime import date


def encode_cursor(d: date, pk: int) -> str:
    b = json.dumps({"d": d.isoformat(), "id": pk}).encode("utf-8")
    return base64.urlsafe_b64encode(b).decode("ascii")

def decode_cursor(cursor: str) -> tuple[date, int]:
    b = base64.urlsafe_b64decode(cursor.encode("ascii"))
    p = json.loads(b.decode("utf-8"))
    return (date.fromisoformat(p["d"]), int(p["id"]))