#!/usr/bin/env python3
"""Build a standalone Claude Scholar study set (one HTML file) from a JSON file.

Usage:
    python3 build_study_set.py study-set.json output.html [--template PATH]

The JSON schema is described in references/schema.md. The script validates the
content, fills in ids, warns about weak spots, and writes a self-contained HTML
file that works offline and sends nothing anywhere.
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys
from collections import Counter

PLACEHOLDER = "__COURSE_JSON__"
MIN_SECTIONS = 2
MIN_QUESTIONS = 6


def clip(value, limit):
    text = re.sub(r"\s+", " ", str(value if value is not None else "")).strip()
    return text[:limit]


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s or "study-set")[:40]


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def normalize(raw):
    """Return (clean_dict, warnings). Exits with a clear message on fatal problems."""
    warnings = []
    if not isinstance(raw, dict):
        fail("Top level of the JSON must be an object.")

    title = clip(raw.get("title"), 70)
    if not title:
        fail('Missing "title".')
    topic = clip(raw.get("topic"), 160) or title
    level = clip(raw.get("level"), 30) or "Beginner"
    blurb = clip(raw.get("blurb"), 200)

    sections_in = raw.get("sections")
    if not isinstance(sections_in, list) or len(sections_in) < MIN_SECTIONS:
        fail(f'"sections" must be a list with at least {MIN_SECTIONS} items.')

    sections, by_ref = [], {}
    for i, s in enumerate(sections_in, 1):
        if not isinstance(s, dict):
            fail(f"Section {i} must be an object.")
        sid = clip(s.get("id"), 20) or f"s{i}"
        if sid in {x["id"] for x in sections}:
            fail(f'Duplicate section id "{sid}".')
        name = clip(s.get("name"), 60)
        if not name:
            fail(f"Section {i} has no name.")
        points = [clip(p, 320) for p in (s.get("points") or []) if clip(p, 320)][:8]
        if not points:
            fail(f'Section "{name}" needs at least one key point.')
        terms = []
        for t in (s.get("terms") or [])[:8]:
            if isinstance(t, dict) and clip(t.get("t"), 80) and clip(t.get("d"), 220):
                terms.append({"t": clip(t["t"], 80), "d": clip(t["d"], 220)})
        sec = {"id": sid, "name": name, "summary": clip(s.get("summary"), 320), "points": points, "terms": terms}
        sections.append(sec)
        by_ref[sid] = sid
        by_ref[name.lower()] = sid
        by_ref[str(i)] = sid
        by_ref[i] = sid

    questions_in = raw.get("questions")
    if not isinstance(questions_in, list):
        fail('"questions" must be a list.')

    questions, seen_ids = [], set()
    for n, q in enumerate(questions_in, 1):
        where = f"Question {n}"
        if not isinstance(q, dict):
            fail(f"{where} must be an object.")
        ref = q.get("s")
        ref_key = ref.lower() if isinstance(ref, str) else ref
        sid = by_ref.get(ref_key) or by_ref.get(ref)
        if sid is None:
            fail(f'{where}: "s" ({ref!r}) does not match any section id, name, or number.')
        text = clip(q.get("q"), 700)
        opts = [clip(o, 280) for o in (q.get("o") or [])]
        ans = q.get("a")
        expl = clip(q.get("x"), 900)
        if not text:
            fail(f'{where}: missing "q".')
        if not (2 <= len(opts) <= 6) or not all(opts):
            fail(f'{where}: "o" needs 2 to 6 non-empty options.')
        if isinstance(ans, bool) or not isinstance(ans, int) or not (0 <= ans < len(opts)):
            fail(f'{where}: "a" must be an integer index into "o" (0 to {len(opts) - 1}).')
        if not expl:
            fail(f'{where}: missing explanation "x".')
        if len({o.lower() for o in opts}) != len(opts):
            warnings.append(f"{where}: duplicate answer options.")
        if any(re.search(r"\b(all|none) of the above\b", o, re.I) for o in opts):
            warnings.append(f'{where}: uses "all/none of the above"; prefer concrete options.')
        qid = clip(q.get("id"), 60)
        if not qid or qid in seen_ids:
            qid = f"{sid}-q{n}"
            while qid in seen_ids:
                qid += "x"
        seen_ids.add(qid)
        questions.append({"id": qid, "s": sid, "q": text, "o": opts, "a": ans, "x": expl})

    if len(questions) < MIN_QUESTIONS:
        fail(f"Need at least {MIN_QUESTIONS} questions; got {len(questions)}.")

    per_sec = Counter(q["s"] for q in questions)
    for sec in sections:
        if per_sec[sec["id"]] == 0:
            warnings.append(f'Section "{sec["name"]}" has no questions.')
        elif per_sec[sec["id"]] < 3:
            warnings.append(f'Section "{sec["name"]}" has only {per_sec[sec["id"]]} question(s).')

    four = [q for q in questions if len(q["o"]) == 4]
    if len(four) >= 8:
        pos = Counter(q["a"] for q in four)
        idx, count = pos.most_common(1)[0]
        if count / len(four) > 0.5:
            warnings.append(
                f"{count} of {len(four)} four-option questions have the correct answer in position "
                f"{'ABCD'[idx]}. Reorder some options so the answer positions vary."
            )

    set_id = clip(raw.get("id"), 80) or f"{slug(title)}-{hashlib.sha1((title + topic).encode()).hexdigest()[:6]}"
    clean = {
        "v": 1, "id": set_id, "title": title, "topic": topic, "level": level, "blurb": blurb,
        "sections": sections, "qs": questions,
    }
    return clean, warnings


def embed(data):
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return (text.replace("</", "<\\/").replace("<!--", "<\\!--")
                .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="study set JSON file")
    ap.add_argument("output", help="HTML file to write")
    ap.add_argument("--template", help="override the template path")
    args = ap.parse_args()

    try:
        raw = json.loads(pathlib.Path(args.input).read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Input file not found: {args.input}")
    except json.JSONDecodeError as e:
        fail(f"Input is not valid JSON: {e}")

    data, warnings = normalize(raw)

    tpl_path = pathlib.Path(args.template) if args.template else pathlib.Path(__file__).resolve().parent.parent / "assets" / "study-set-template.html"
    try:
        tpl = tpl_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail(f"Template not found: {tpl_path}")
    if tpl.count(PLACEHOLDER) != 1:
        fail(f"Template must contain {PLACEHOLDER} exactly once.")

    html = tpl.replace(PLACEHOLDER, embed(data)).replace("<title>Study set</title>", f"<title>{_esc(data['title'])}</title>", 1)
    out = pathlib.Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    per = Counter(q["s"] for q in data["qs"])
    print(f'Built "{data["title"]}" ({data["level"]}) -> {out}')
    print(f'{len(data["sections"])} sections, {len(data["qs"])} questions, id {data["id"]}')
    for s in data["sections"]:
        print(f'  - {s["name"]}: {per[s["id"]]} questions, {len(s["points"])} key points, {len(s["terms"])} terms')
    for w in warnings:
        print(f"WARNING: {w}")


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    main()
