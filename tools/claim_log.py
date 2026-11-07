"""Claim log for an episode's script: every sentence that states a checkable fact, ready for the fact-check.

    python tools/claim_log.py neom-the-line        # writes episodes/<slug>/factcheck.md (keeps an existing one)

A sentence is a claim when it has a number, a year or date, a currency or percentage, an attribution ("said",
"reported", "according to") or a causal word. Stat cards and chart values are listed too, because they put
numbers on screen. The fact-check skill fills the Source and Status columns from research.md.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
from schema import load_script  # noqa: E402

CHECKABLE = re.compile(
    r"\d|\b(one|two|three|four|five|six|seven|eight|nine|ten|twenty|hundred|thousand|million|billion|trillion|"
    r"half|third|double|twice|percent)\b|\b(January|February|March|April|May|June|July|August|September|October|"
    r"November|December)\b|\b(said|says|reported|according|announced|denied|confirmed|estimated|found|warned|"
    r"told|claimed)\b|\b(because|caused|led to|so that)\b", re.IGNORECASE)
SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")


def main():
    slug = sys.argv[1]
    out = ROOT / "episodes" / slug / "factcheck.md"
    if out.exists() and "--force" not in sys.argv:
        sys.exit(f"{out.relative_to(ROOT)} exists (pass --force to rewrite it)")
    script = load_script(ROOT / "episodes" / slug / "script.json")
    rows, n = [], 0
    for ci, ch in enumerate(script.chapters, 1):
        for pi, p in enumerate(ch.paragraphs, 1):
            for sentence in SENTENCE.split(p.text):
                if CHECKABLE.search(sentence):
                    n += 1
                    rows.append(f"| {n} | c{ci:02d}p{pi:02d} | narration | {sentence.strip()} | | |")
            for s in p.shots:
                if s.stat:
                    n += 1
                    text = f"{s.stat.value}: {s.stat.label}" + (f" ({s.stat.note})" if s.stat.note else "")
                    rows.append(f"| {n} | c{ci:02d}p{pi:02d} | stat card | {text} | {s.stat.source or ''} | |")
                if s.chart:
                    n += 1
                    vals = ", ".join(f"{k} {v:g}" for k, v in s.chart.data)
                    rows.append(f"| {n} | c{ci:02d}p{pi:02d} | chart | {s.chart.title}: {vals} | {s.chart.source or ''} | |")
                if s.on_screen_text and CHECKABLE.search(s.on_screen_text):
                    n += 1
                    rows.append(f"| {n} | c{ci:02d}p{pi:02d} | on screen | {s.on_screen_text} | | |")
    head = [f"# {slug} - fact-check", "",
            "Status: verified (primary source) | attributed (secondary source, said in the script as \"X reported\") | "
            "own (our measurement or calculation, reproducible) | FIX (wrong, unsupported or quoted without the "
            "original text). Sources: R-items of research.md or a URL.", "",
            "| # | Where | Kind | Claim | Source | Status |", "|---|---|---|---|---|---|"]
    out.write_text("\n".join(head + rows) + "\n", encoding="utf-8")
    print(f"{n} claims -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
