"""Short for jakarta-sinking: Indonesia built a new capital because Jakarta sinks, and Jakarta is still the capital.
All facts from episodes/jakarta-sinking research.md and verification.md.  python build_script.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
AFTER = "2026-06-01/2026-10-31"


def place(name, lon, lat, label, kind="city"):
    return {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label}


PALACE = place("Garuda Palace", 116.6962, -0.9587, "GARUDA PALACE", "site")
JAKARTA = place("Jakarta", 106.8272, -6.1754, "JAKARTA", "capital")
MOVE = {"from": [106.8272, -6.1754], "to": [116.6962, -0.9587], "mode": "line", "seconds": 3, "label": "To Borneo"}


def m(text, *steps, at=0, cut=True):
    s = {"type": "map", "at": at, "map": {"steps": list(steps)}, "on_screen_text": text}
    if cut:
        s["map"]["cut"] = True
    return s


def v(lon, lat, span, date=AFTER, **kw):
    d = {"view": {"lon": lon, "lat": lat, "span": span}, **kw}
    if span <= 2:
        d["date"] = date
    return d


def P(text, *shots):
    return {"text": text, "shots": list(shots)}


paragraphs = [
    P("Jakarta is sinking, in places many times faster than the sea is rising. So in 2019 Indonesia decided to move its capital.",
      m("Jakarta is sinking", v(106.80, -6.11, 0.12, places=[JAKARTA])),
      m("Move the capital", v(112.0, -3.5, 16, places=[JAKARTA, PALACE], routes=[MOVE]), at="So in")),
    P("Here, to the forest of Borneo. This is the site in 2019. And this is the same place this year.",
      m("Nusantara · Sentinel-2",
        {**v(116.696, -0.959, 0.12), "compare": {"before": "2019-03-19", "after": "2026-08-16", "seconds": 2.2, "until": "And this"}},
        {"at": "And this", "places": [PALACE]}, cut=False)),
    P("The money has shrunk year by year: forty-three trillion rupiah in 2024, six point three trillion this year.",
      m("2024: Rp 43 trillion", v(116.70, -0.965, 0.05), at="forty-three"),
      m("2026: Rp 6.3 trillion", v(116.715, -0.95, 0.07), at="six point")),
    P("About ten thousand people have moved in, not the half a million once planned.",
      m("~10,000 people, not 500,000", v(116.69, -0.975, 0.06, places=[PALACE]))),
    P("And in May, the Constitutional Court ruled that Jakarta stays the capital until a decree moves it.",
      m("May 2026: the court rules", v(106.83, -6.17, 0.08, places=[JAKARTA])),
      m("By law, Jakarta is still the capital", v(106.80, -6.15, 0.2), at="until a")),
    P("Should Indonesia finish the new capital, or save the old one?",
      m("Finish it, or save Jakarta?", v(113.5, -2.8, 11, places=[JAKARTA, PALACE]))),
]

script = {
    "title": "Indonesia Built a New Capital. Jakarta Is Still the Capital",
    "format": "short",
    "voice": "am_michael",
    "music": "procedural",
    "map_style": "satellite",
    "captions": True,
    "sources": ["All facts from episodes/jakarta-sinking research.md and verification.md (ABC News Oct 2026, The Jakarta Post, Constitutional Court ruling May 2026)."],
    "thumbnail": {"text": "NOT THE CAPITAL", "focus": [116.696, -0.959, 0.12]},
    "chapters": [{"title": "The Capital That Stalled", "mood": "tension", "paragraphs": paragraphs}],
    "youtube": {
        "title": "Indonesia Built a New Capital. Jakarta Is Still the Capital",
        "description": "Because Jakarta is sinking, Indonesia decided in 2019 to move its capital to Nusantara on Borneo. From orbit, the forest site in 2019 and 2026. The budget fell from Rp 43 trillion in 2024 to Rp 6.3 trillion in 2026, about 10,000 people have moved in, and a court ruled in May 2026 that Jakarta stays the capital until a decree moves it.\n\nFull documentary on the channel: Sinking Jakarta\n\n#geography #satellite #indonesia",
        "tags": ["Nusantara", "Indonesia new capital", "Jakarta", "IKN", "Borneo", "sinking city", "satellite images", "before and after", "Sentinel-2", "shorts"],
        "pinned_comment": "Should Indonesia finish the new capital, or spend the money saving Jakarta?",
    },
}
(HERE / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(sum(len(p["text"].split()) for p in paragraphs), "words")
