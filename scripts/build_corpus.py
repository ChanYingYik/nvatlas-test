#!/usr/bin/env python3
"""Build the browser-ready NV Atlas corpus from the supplied CSV.

The source text, translation, nominal and Chinese verb are preserved exactly.
Only analysis metadata is added, using the rules documented in codebook.html.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_CSV = ROOT / "NVAtlas-AI-Agent.csv"
OUTPUT_JSON = ROOT / "data" / "corpus.json"
SOURCE_FILE_DATE = "2026-10-30"

COMMUNICATION = {
    "announcement",
    "argument",
    "communication",
    "compliment",
    "confession",
    "conversation",
    "declaration",
    "description",
    "discussion",
    "equivocation",
    "explanation",
    "expression",
    "grievance",
    "information",
    "interpretation",
    "lecture",
    "mention",
    "notion",
    "objection",
    "persuasion",
    "petition",
    "preachment",
    "pronouncement",
    "question",
    "recitation",
    "recommendation",
    "recognition",
    "recollection",
    "reference",
    "sentence",
    "suggestion",
}

CONTROL = {
    "absolution",
    "admission",
    "administration",
    "annulment",
    "appointment",
    "arrangement",
    "authorization",
    "capture",
    "cessation",
    "confiscation",
    "consideration",
    "conviction",
    "decision",
    "defence",
    "detention",
    "election",
    "evidence",
    "examination",
    "exception",
    "execution",
    "expulsion",
    "indictment",
    "inspection",
    "management",
    "obedience",
    "offence",
    "permission",
    "probation",
    "prosecution",
    "protection",
    "punishment",
    "ration",
    "registration",
    "reservation",
    "resignation",
    "resistance",
    "retirement",
    "settlement",
    "signature",
    "suspension",
    "violation",
}

AFFECT = {
    "admiration",
    "amusement",
    "attention",
    "dedication",
    "dependence",
    "devotion",
    "disappointment",
    "excitement",
    "fixation",
    "fulfillment",
    "impression",
    "indulgence",
    "inspiration",
    "intention",
    "intoxication",
    "obsession",
    "passion",
    "pleasure",
    "preference",
    "relaxation",
    "reputation",
    "resemblance",
    "satisfaction",
    "sensation",
    "silence",
    "temptation",
    "torment",
    "torture",
    "trance",
    "vengeance",
}

CATEGORY_BY_TERM = {
    **{term: "communication" for term in COMMUNICATION},
    **{term: "control" for term in CONTROL},
    **{term: "affect" for term in AFFECT},
}

MODAL_MARKERS = (
    "不",
    "没",
    "别",
    "要",
    "会",
    "能",
    "可",
    "请",
    "让",
    "敢",
    "想",
    "得",
    "必须",
    "应该",
    "可以",
)


def classify(term: str) -> str:
    """Apply the documented four-way semantic rule."""
    return CATEGORY_BY_TERM.get(term.casefold(), "process")


def realization(target: str, verb: str) -> str:
    """Describe where the Chinese verb occurs in the sentence."""
    clean = target.strip(" \t\r\n-—–…,.!?:;\"'“”‘’《》()（）")
    index = clean.find(verb)
    if index <= 0:
        return "verb-first"
    prefix = clean[:index]
    tail = prefix[-4:]
    if any(marker in tail for marker in MODAL_MARKERS):
        return "modulated"
    return "embedded"


def main() -> None:
    with SOURCE_CSV.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))

    required = {"id", "English", "Chinese", "English_Nominal", "Chinese_Verb"}
    if len(rows) != 500:
        raise ValueError(f"Expected 500 entries, found {len(rows)}")
    if set(rows[0]) != required:
        raise ValueError(f"Unexpected CSV columns: {sorted(rows[0])}")
    if any(not value.strip() for row in rows for value in row.values()):
        raise ValueError("The supplied CSV contains an empty required value")

    entries = []
    for row in rows:
        category = classify(row["English_Nominal"])
        entries.append(
            {
                "id": row["id"],
                "source_text": row["English"],
                "target_text": row["Chinese"],
                "source": (
                    "OpenSubtitles 2024 en-zh_CN, sentence id "
                    f"{row['id']}; user-supplied CSV dated {SOURCE_FILE_DATE}; "
                    "exact collection date not supplied"
                ),
                "category": category,
                "human_checked": "no",
                "unit": "sentence pair",
                "key_term": row["English_Nominal"],
                "target_verb": row["Chinese_Verb"],
                "realization": realization(row["Chinese"], row["Chinese_Verb"]),
                "genre": "subtitles",
                "corpus_version": "2024",
                "collection_date": "not supplied",
                "source_file_date": SOURCE_FILE_DATE,
            }
        )

    category_counts = Counter(entry["category"] for entry in entries)
    realization_counts = Counter(entry["realization"] for entry in entries)
    duplicate_pairs = sum(
        count - 1 for count in Counter(
            (entry["source_text"], entry["target_text"]) for entry in entries
        ).values()
    )

    payload = {
        "meta": {
            "title_en": "Nominal / Verb: Translation Patterns in English-Chinese Subtitles",
            "title_zh": "名詞／動詞：英中字幕翻譯模式",
            "corpus": "OpenSubtitles 2024 en-zh_CN",
            "supplied_file": SOURCE_CSV.name,
            "collection_date": "not supplied",
            "source_file_date": SOURCE_FILE_DATE,
            "entry_count": len(entries),
            "verified_count": 0,
            "verification_target": 50,
            "duplicate_pair_count": duplicate_pairs,
            "category_counts": dict(category_counts),
            "realization_counts": dict(realization_counts),
            "provenance_note": (
                "The 500 sentence pairs and sentence IDs came from the student's "
                "NVAtlas-AI-Agent.csv. The OpenSubtitles label is inferred from the "
                "course corpus example and the supplied sentence IDs; it should be "
                "confirmed by the student against the original download."
            ),
            "classification_note": (
                "Categories use the semantic-field rules published in codebook.html. "
                "They are analysis metadata, not source-corpus metadata."
            ),
        },
        "entries": entries,
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(entries)} entries to {OUTPUT_JSON.relative_to(ROOT)}")
    print("Categories:", dict(sorted(category_counts.items())))
    print("Realizations:", dict(sorted(realization_counts.items())))
    print("Duplicate sentence pairs retained:", duplicate_pairs)


if __name__ == "__main__":
    main()
