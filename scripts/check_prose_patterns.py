#!/usr/bin/env python3
r"""Advisory detector of paragraph-scale patterns that per-sentence review misses.

Each sentence of a passage can be correct alone while the passage, read in
order, restates what the reader has just been told, repeats one template, or
copies its figure captions.  The canon names these failures (narrative.md:
given information, template runs, redundancy and balance); this script finds
the mechanical candidates so that a reviewer judges evidence instead of
searching for it.  It reports, per paragraph:

1. **Repeated phrases** -- a multiword technical phrase (an allowed name of at
   least ``--min-words`` words of the project registry when ``--registry`` is
   given, else a 3--6-word noun phrase) that occurs in full three or more times within one
   paragraph, or occurs in full again in the paragraph right after its
   definition.
2. **Template runs** -- three or more consecutive sentences of one paragraph,
   or three or more consecutive paragraphs, that open with the same first
   three words or the same first two content words.
3. **Caption--text overlap** -- for each figure or table caption, the longest
   word sequence (at least eight words) that it shares with a paragraph that
   references the figure.

A whole-file run also prints a summary line: the most frequent opening word and
the counts of common connectives.  The output is evidence for the sentence,
terminology, and holistic reviewers, never a verdict: a repeated name can be
needed to avoid ambiguity, and a run can be a genuinely parallel display.

Usage::

    python3 check_prose_patterns.py FILE [--registry project-vocabulary.json]
        [--min-words 3] [--lines A-B] [--json] [--min-repeats 3] [--min-run 3]
        [--min-overlap 8]

LaTeX comments (and Markdown ``<!-- -->`` comments) are removed first.  The
exit code is 0 whenever the file could be read.  Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import check_edit_round as cer


#: Function words: a phrase may not start or end with one, and they are skipped
#: when the first content words of a sentence are taken.
STOP = frozenset("""
a an the of in on at to for from by with and or but nor so as than that this these
those which who whom whose what when where while if then thus hence also only both
each every all any some such its it their there here is are was were be been being
has have had do does did can could may might must shall should will would not no we
our us one two into onto over under between through per via about after before
during upon within without whether however more most less same other
ref refs sec secs fig figs eq eqs appendix table
""".split())

#: Words that signal that a sentence defines the phrase it contains.
DEFINITION_CUE = re.compile(
    r"\b(define[sd]?|call(?:ed|s)?|denote[sd]?|refer(?:red)? to|term(?:ed)?|"
    r"name[sd]?|we write)\b", re.I)

#: Connectives counted in the summary line (label, pattern on lower-case plain text).
CONNECTIVES = (
    (", so", r",\s+so\b"), ("also", r"\balso\b"), ("however", r"\bhowever\b"),
    ("but", r"\bbut\b"), ("although/though", r"\b(?:although|though)\b"),
    ("whereas/while", r"\b(?:whereas|while)\b"), ("instead", r"\binstead\b"),
    ("because", r"\bbecause\b"), ("thus/hence/therefore", r"\b(?:thus|hence|therefore)\b"),
)

FLOAT_RE = re.compile(r"\\begin\{(figure|table)\*?\}.*?\\end\{\1\*?\}", re.S)
CAPTION_RE = re.compile(r"\\caption\*?(?:\[[^\]]*\])?\{")
LABEL_RE = re.compile(r"\\label\{([^}]*)\}")
REF_RE = re.compile(r"\\(?:ref|cref|Cref|autoref|subref|figref|tabref|eqref)\*?\{([^}]*)\}")
CITE_RE = re.compile(r"\\(?:cite[a-z]*|label)\*?(?:\[[^\]]*\])*\{[^}]*\}")
UNWRAP_RE = re.compile(r"\\(?:emph|textit|textbf|text|mathrm|textrm)\{([^{}]*)\}")
COMMAND_RE = re.compile(r"\\[A-Za-z]+\*?")


# ---------------------------------------------------------------------------
# reading the file
# ---------------------------------------------------------------------------

def strip_comments(text: str, fmt: str) -> str:
    r"""Remove comments and keep the line count.

    Parameters
    ----------
    text : str
        Raw file content.
    fmt : str
        ``"latex"`` or ``"markdown"``.

    Returns
    -------
    str
        The text without comments; every removed line break is kept, so line
        numbers stay those of the file.
    """
    if fmt == "markdown":
        return re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    return "\n".join(cer.strip_comment(line) for line in text.splitlines())


def balanced(text: str, start: int) -> str:
    r"""Content of a brace group whose opening brace is just before ``start``.

    Parameters
    ----------
    text : str
        Text that contains the group.
    start : int
        Index of the first character after the opening brace.

    Returns
    -------
    str
        The content up to the matching closing brace (to the end if unmatched).
    """
    depth = 1
    for i in range(start, len(text)):
        if text[i] == "{" and text[i - 1] != "\\":
            depth += 1
        elif text[i] == "}" and text[i - 1] != "\\":
            depth -= 1
            if depth == 0:
                return text[start:i]
    return text[start:]


def paragraphs_of(text: str, fmt: str = "latex") -> list[dict]:
    r"""Cut a file into the paragraphs and captions the detector reads.

    Floats are taken out first, so that a caption is its own paragraph and the
    rest of the float (graphics, tabular cells) is not read.  The remaining
    text is cut by :func:`check_edit_round.split_units`, the same cut the
    section skill uses for its chunks.

    Parameters
    ----------
    text : str
        Raw file content.
    fmt : str, optional
        ``"latex"`` (default) or ``"markdown"``.

    Returns
    -------
    list of dict
        In reading order, one dict per paragraph with ``kind`` (``prose``,
        ``item`` or ``caption``), ``start`` and ``end`` (1-based lines),
        ``sentences`` (raw sentences), ``labels`` (captions) and ``refs``
        (labels the paragraph references).
    """
    body = strip_comments(text, fmt)
    captions: list[dict] = []

    def take_float(match: re.Match) -> str:
        """Record the captions of one float and blank it out."""
        block = match.group(0)
        line = body.count("\n", 0, match.start()) + 1
        labels = LABEL_RE.findall(block)
        for cap in CAPTION_RE.finditer(block):
            content = balanced(block, cap.end())
            captions.append({"kind": "caption", "start": line,
                             "end": line + block.count("\n"), "labels": labels,
                             "sentences": cer.split_sentences(content, raw=True), "refs": set()})
        return "\n" * block.count("\n")

    if fmt == "latex":
        body = FLOAT_RE.sub(take_float, body)
    else:
        body = re.sub(r"(?m)^#{1,6}\s.*$", "", body)
    paras = []
    for unit in cer.split_units(body.splitlines()):
        refs = {lab.strip() for m in REF_RE.finditer(unit["text"]) for lab in m.group(1).split(",")}
        paras.append({"kind": unit["kind"], "start": unit["start"], "end": unit["end"],
                      "labels": [], "sentences": unit["raw_sentences"], "refs": refs})
    return sorted(paras + captions, key=lambda p: (p["start"], p["kind"] != "caption"))


# ---------------------------------------------------------------------------
# tokens
# ---------------------------------------------------------------------------

def segments(raw: str) -> list[list[str]]:
    r"""Word runs of a sentence that a noun phrase can span.

    Math, references, and punctuation inside the sentence break a run, so that
    a phrase is never assembled across an equation or a comma.

    Parameters
    ----------
    raw : str
        One raw sentence.

    Returns
    -------
    list of list of str
        Lower-case word runs.
    """
    t = cer.MATH_RE.sub(" | ", raw)
    t = REF_RE.sub(" | ", t)
    t = CITE_RE.sub(" | ", t)
    for _ in range(3):
        t = UNWRAP_RE.sub(r"\1", t)
    t = COMMAND_RE.sub(" ", t).replace("~", " ")
    out = []
    for part in re.split(r"[|,;:()\[\]{}.!?\"]", t.lower()):
        words = re.findall(r"[a-z][a-z'\-]*[a-z]|[a-z]", part)
        if words:
            out.append(words)
    return out


def words(raw: str) -> list[str]:
    r"""All words of a sentence in order (math and references dropped).

    Parameters
    ----------
    raw : str
        One raw sentence.

    Returns
    -------
    list of str
        Lower-case words.
    """
    return [w for seg in segments(raw) for w in seg]


def overlap_tokens(raw: str) -> list[str]:
    r"""Tokens for comparing a caption with the text.

    Unlike :func:`words`, a math expression stays as one token (its source with
    blanks removed), so that a repeated number or formula counts as shared.

    Parameters
    ----------
    raw : str
        Raw text.

    Returns
    -------
    list of str
        Lower-case tokens.
    """
    toks: list[str] = []
    pos = 0
    # Prose between math spans is cleaned of markup; each math span is one token.
    for m in list(cer.MATH_RE.finditer(raw)) + [None]:
        t = raw[pos:m.start() if m else len(raw)]
        t = REF_RE.sub(" 0ref0 ", t)
        t = CITE_RE.sub(" ", t)
        for _ in range(3):
            t = UNWRAP_RE.sub(r"\1", t)
        t = COMMAND_RE.sub(" ", t).replace("~", " ")
        toks += [x.lower().rstrip(".") for x in re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-.%]*", t)]
        if m:
            toks.append(re.sub(r"\s+", "", m.group(0)))
            pos = m.end()
    return toks


def count_phrase(phrase: tuple[str, ...], segs: list[list[str]]) -> int:
    r"""Occurrences of a word sequence inside word runs.

    Parameters
    ----------
    phrase : tuple of str
        The words of the phrase.
    segs : list of list of str
        Word runs (:func:`segments`).

    Returns
    -------
    int
        Number of (possibly overlapping) occurrences.
    """
    n = len(phrase)
    return sum(1 for seg in segs for i in range(len(seg) - n + 1) if tuple(seg[i:i + n]) == phrase)


def ngrams(segs: list[list[str]], low: int = 3, high: int = 6) -> Counter:
    r"""Candidate noun phrases of some word runs and their counts.

    A candidate has ``low`` to ``high`` words, none of a single letter, and does
    not start or end with a function word.

    Parameters
    ----------
    segs : list of list of str
        Word runs.
    low, high : int, optional
        Phrase lengths.

    Returns
    -------
    Counter
        ``{phrase tuple: count}``.
    """
    out: Counter = Counter()
    for seg in segs:
        for n in range(low, high + 1):
            for i in range(len(seg) - n + 1):
                g = tuple(seg[i:i + n])
                if g[0] in STOP or g[-1] in STOP or any(len(w) < 2 for w in g):
                    continue
                out[g] += 1
    return out


def contains(longer: tuple[str, ...], shorter: tuple[str, ...]) -> bool:
    r"""Whether ``shorter`` is a contiguous part of ``longer``.

    Parameters
    ----------
    longer, shorter : tuple of str
        Word sequences.

    Returns
    -------
    bool
        True if ``shorter`` occurs in ``longer`` and is strictly shorter.
    """
    n = len(shorter)
    return n < len(longer) and any(longer[i:i + n] == shorter for i in range(len(longer) - n + 1))


def registry_phrases(path: Path | None, min_words: int = 3) -> list[tuple[str, ...]]:
    r"""Multiword allowed names of a vocabulary registry.

    A two-word name is usually already the short form the given-information
    rule asks for, so by default only names of three or more words count.

    Parameters
    ----------
    path : Path or None
        ``project-vocabulary.json``; None for no registry.
    min_words : int, optional
        Fewest words of a reported name.

    Returns
    -------
    list of tuple of str
        Each long enough name (``term`` and ``allowed_names``) as words.
    """
    if path is None:
        return []
    terms = json.loads(Path(path).read_text()).get("terms", [])
    names = {n for e in terms for n in [e.get("term", "")] + list(e.get("allowed_names") or [])}
    out = {tuple(words(n)) for n in names if n}
    return sorted(p for p in out if len(p) >= min_words)


# ---------------------------------------------------------------------------
# the three detectors
# ---------------------------------------------------------------------------

def defined_in(phrase: tuple[str, ...], para: dict) -> bool:
    r"""Whether a paragraph defines a phrase.

    A phrase is defined where it is emphasized (``\emph``, ``\textit``,
    Markdown ``*...*``) or where it occurs in a sentence with a definition cue
    ("we define", "is called", "denote", ...).

    Parameters
    ----------
    phrase : tuple of str
        Words of the phrase.
    para : dict
        A paragraph of :func:`paragraphs_of`.

    Returns
    -------
    bool
        True if the paragraph defines it.
    """
    for raw in para["sentences"]:
        emph = re.findall(r"\\(?:emph|textit)\{([^{}]*)\}|(?<!\*)\*([^*]+)\*(?!\*)", raw)
        if any(tuple(words(a or b)) == phrase or contains(tuple(words(a or b)), phrase)
               for a, b in emph):
            return True
        if DEFINITION_CUE.search(raw) and count_phrase(phrase, segments(raw)):
            return True
    return False


def repeated_phrases(paras: list[dict], registry: list[tuple[str, ...]],
                     min_repeats: int = 3) -> list[dict]:
    r"""Technical phrases restated in full inside a paragraph or right after their definition.

    Parameters
    ----------
    paras : list of dict
        Output of :func:`paragraphs_of`.
    registry : list of tuple of str
        Multiword registry names; when empty, frequent 3--6-word noun phrases
        are the candidates instead.
    min_repeats : int, optional
        Full occurrences within one paragraph that make a finding.

    Returns
    -------
    list of dict
        Findings with ``type`` (``within_paragraph`` or ``after_definition``),
        ``phrase``, ``count``, ``start``, ``end`` and, for the second type,
        ``defined_at``.
    """
    segs = [[s for raw in p["sentences"] for s in segments(raw)] for p in paras]
    if registry:
        counts = [Counter({ph: c for ph in registry if (c := count_phrase(ph, sg))}) for sg in segs]
    else:
        counts = [ngrams(sg) for sg in segs]
    findings: list[dict] = []
    for i, p in enumerate(paras):
        hits = {ph: c for ph, c in counts[i].items() if c >= min_repeats}
        for ph, c in hits.items():
            if any(contains(q, ph) and hits[q] >= c for q in hits):
                continue
            findings.append({"type": "within_paragraph", "phrase": " ".join(ph), "count": c,
                             "start": p["start"], "end": p["end"]})
    prose = [i for i, p in enumerate(paras) if p["kind"] != "caption"]
    seen: set[tuple[str, ...]] = set()
    for a, b in zip(prose, prose[1:]):
        cands = [ph for ph in counts[a] if ph in counts[b] and ph not in seen]
        for ph in cands:
            if defined_in(ph, paras[a]):
                seen.add(ph)
        later = [ph for ph in cands if ph in seen]
        for ph in later:
            if any(contains(q, ph) for q in later):
                continue
            findings.append({"type": "after_definition", "phrase": " ".join(ph),
                             "count": counts[b][ph], "start": paras[b]["start"],
                             "end": paras[b]["end"], "defined_at": paras[a]["start"]})
    return sorted(findings, key=lambda f: f["start"])


def opening_keys(raw: str) -> tuple[tuple[str, ...] | None, tuple[str, ...] | None]:
    r"""Template keys of a sentence opening.

    Parameters
    ----------
    raw : str
        One raw sentence.

    Returns
    -------
    tuple
        ``(first three words, first two content words)``; an entry is None when
        the sentence has too few words.
    """
    w = words(raw)
    content = [x for x in w if x not in STOP]
    return (tuple(w[:3]) if len(w) >= 3 else None,
            tuple(content[:2]) if len(content) >= 2 else None)


def runs(keys: list[tuple], min_run: int) -> list[tuple[int, int, int, tuple]]:
    r"""Maximal runs of equal keys.

    Parameters
    ----------
    keys : list of tuple
        One ``(first-three key, content key)`` pair per item.
    min_run : int
        Shortest reported run.

    Returns
    -------
    list of tuple
        ``(first index, last index, key type, key)``; a content-word run inside
        a first-three-word run is not repeated.
    """
    found = []
    for kind in (0, 1):
        i = 0
        while i < len(keys):
            j = i
            while j + 1 < len(keys) and keys[i][kind] is not None and keys[j + 1][kind] == keys[i][kind]:
                j += 1
            if keys[i][kind] is not None and j - i + 1 >= min_run:
                if not (kind == 1 and any(f[0] <= i and j <= f[1] for f in found)):
                    found.append((i, j, kind, keys[i][kind]))
            i = j + 1
    return found


def template_runs(paras: list[dict], min_run: int = 3) -> list[dict]:
    r"""Runs of sentences, or of paragraphs, that open with one template.

    Parameters
    ----------
    paras : list of dict
        Output of :func:`paragraphs_of`.
    min_run : int, optional
        Shortest reported run.

    Returns
    -------
    list of dict
        Findings with ``type`` (``sentences`` or ``paragraphs``), ``length``,
        ``opening``, ``key`` (``first words`` or ``content words``), ``start``,
        ``end`` and, for sentences, ``sentences`` (1-based indices in the
        paragraph).
    """
    out = []
    label = ("first words", "content words")
    for p in paras:
        if p["kind"] == "caption":
            continue
        for i, j, kind, key in runs([opening_keys(s) for s in p["sentences"]], min_run):
            out.append({"type": "sentences", "length": j - i + 1, "opening": " ".join(key),
                        "key": label[kind], "start": p["start"], "end": p["end"],
                        "sentences": [i + 1, j + 1]})
    prose = [p for p in paras if p["kind"] != "caption" and p["sentences"]]
    for i, j, kind, key in runs([opening_keys(p["sentences"][0]) for p in prose], min_run):
        out.append({"type": "paragraphs", "length": j - i + 1, "opening": " ".join(key),
                    "key": label[kind], "start": prose[i]["start"], "end": prose[j]["end"]})
    return out


def longest_shared(a: list[str], b: list[str]) -> list[str]:
    r"""Longest contiguous token sequence common to two token lists.

    Parameters
    ----------
    a, b : list of str
        Token lists.

    Returns
    -------
    list of str
        The longest shared sequence (the first one found when several tie).
    """
    best, end = 0, 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best, end = cur[j], i
        prev = cur
    return a[end - best:end]


def caption_overlap(paras: list[dict], min_overlap: int = 8) -> list[dict]:
    r"""Word sequences that a caption shares with the text that references its float.

    Parameters
    ----------
    paras : list of dict
        Output of :func:`paragraphs_of`.
    min_overlap : int, optional
        Shortest reported shared sequence, in tokens.

    Returns
    -------
    list of dict
        Findings with ``label``, ``caption_start``, ``start``, ``end`` (the
        citing paragraph), ``length`` and ``shared`` (the shared words).
    """
    out = []
    for cap in (p for p in paras if p["kind"] == "caption" and p["labels"]):
        ctoks = overlap_tokens(" ".join(cap["sentences"]))
        for p in paras:
            if p["kind"] == "caption" or not (p["refs"] & set(cap["labels"])):
                continue
            shared = longest_shared(ctoks, overlap_tokens(" ".join(p["sentences"])))
            if len(shared) >= min_overlap:
                out.append({"label": cap["labels"][0], "caption_start": cap["start"],
                            "start": p["start"], "end": p["end"], "length": len(shared),
                            "shared": " ".join(shared)})
    return out


def references(text: str, fmt: str = "latex", min_refs: int = 3) -> list[dict]:
    r"""Items that the text refers to several times.

    Equations are left out: a repeated reference to a figure, table, section or
    appendix is the one a reader notices.

    Parameters
    ----------
    text : str
        Raw file content.
    fmt : str, optional
        ``"latex"`` or ``"markdown"``; Markdown has no references.
    min_refs : int, optional
        Fewest references that are reported.

    Returns
    -------
    list of dict
        One finding per item, with ``label``, ``count`` and ``lines``.
    """
    if fmt != "latex":
        return []
    found: dict[str, list[int]] = {}
    for no, line in enumerate(strip_comments(text, fmt).splitlines(), 1):
        for match in REF_RE.finditer(line):
            for label in match.group(1).split(","):
                label = label.strip()
                if not label.lower().startswith("eq"):
                    found.setdefault(label, []).append(no)
    return [{"label": k, "count": len(v), "lines": v}
            for k, v in sorted(found.items()) if len(v) >= min_refs]


def summary(paras: list[dict]) -> dict:
    r"""Opening-word share and connective counts of the whole text.

    Parameters
    ----------
    paras : list of dict
        Output of :func:`paragraphs_of`.

    Returns
    -------
    dict
        ``sentences`` (count), ``top_opening`` (word), ``top_share`` (fraction)
        and ``connectives`` (label to count).
    """
    sents = [s for p in paras if p["kind"] != "caption" for s in p["sentences"]]
    firsts = Counter(w[0] for s in sents if (w := words(s)))
    plain = " ".join(cer.plain_text(s) for s in sents).lower()
    top, n = firsts.most_common(1)[0] if firsts else ("", 0)
    return {"sentences": len(sents), "top_opening": top,
            "top_share": round(n / len(sents), 2) if sents else 0.0,
            "connectives": {lab: len(re.findall(pat, plain)) for lab, pat in CONNECTIVES}}


def analyze(text: str, fmt: str = "latex", registry: list[tuple[str, ...]] | None = None,
            min_repeats: int = 3, min_run: int = 3, min_overlap: int = 8) -> dict:
    r"""Run the three detectors and the summary on one file.

    Parameters
    ----------
    text : str
        Raw file content.
    fmt : str, optional
        ``"latex"`` or ``"markdown"``.
    registry : list of tuple of str, optional
        Multiword registry names (:func:`registry_phrases`).
    min_repeats, min_run, min_overlap : int, optional
        Thresholds of the three detectors.

    Returns
    -------
    dict
        ``repeated_phrases``, ``template_runs``, ``caption_overlap`` (lists of
        findings), ``references`` and ``summary``.
    """
    paras = paragraphs_of(text, fmt)
    return {"repeated_phrases": repeated_phrases(paras, registry or [], min_repeats),
            "template_runs": template_runs(paras, min_run),
            "caption_overlap": caption_overlap(paras, min_overlap),
            "references": references(text, fmt),
            "summary": summary(paras)}


def restrict(result: dict, first: int, last: int) -> dict:
    r"""Keep the findings that touch a range of lines.

    Parameters
    ----------
    result : dict
        Output of :func:`analyze`.
    first, last : int
        1-based inclusive line range.

    Returns
    -------
    dict
        The same structure with only the findings whose paragraph (or, for a
        caption overlap, whose caption or citing paragraph) meets the range;
        the summary and the references, which are counted over the whole
        text, are dropped.
    """
    def meets(f: dict) -> bool:
        """Whether a finding touches the range."""
        hit = f["start"] <= last and f["end"] >= first
        return hit or ("caption_start" in f and first <= f["caption_start"] <= last)

    return {k: [f for f in v if meets(f)] for k, v in result.items()
            if k not in ("summary", "references")}


def span(f: dict) -> str:
    r"""Line span of a finding, as ``L12`` or ``L12-15``.

    Parameters
    ----------
    f : dict
        A finding with ``start`` and ``end``.

    Returns
    -------
    str
        The span label.
    """
    return f"L{f['start']}" + (f"-{f['end']}" if f["end"] != f["start"] else "")


def format_report(result: dict) -> str:
    r"""Plain-text report of :func:`analyze` or :func:`restrict`.

    Parameters
    ----------
    result : dict
        Detector output.

    Returns
    -------
    str
        One line per finding under three headings; ``(none)`` when empty.
    """
    lines = []
    s = result.get("summary")
    if s and s["sentences"]:
        conn = ", ".join(f'"{k}" {v}' for k, v in s["connectives"].items())
        lines.append(f"Summary: {s['sentences']} sentences; {round(100 * s['top_share'])}% open "
                     f"with \"{s['top_opening']}\"; connectives: {conn}")
    lines.append("Repeated phrases (given information restated in full?)")
    for f in result["repeated_phrases"]:
        where = f"  {span(f)}: \"{f['phrase']}\" "
        if f["type"] == "within_paragraph":
            lines.append(where + f"{f['count']} times in this paragraph")
        else:
            lines.append(where + f"in full again in the paragraph after its definition "
                         f"(L{f['defined_at']})")
    if not result["repeated_phrases"]:
        lines.append("  (none)")
    lines.append("Template runs (shared opening; frame or genuine parallel display?)")
    for f in result["template_runs"]:
        if f["type"] == "sentences":
            a, b = f["sentences"]
            lines.append(f"  {span(f)}, sentences {a}-{b}: {f['length']} consecutive "
                         f"sentences open with the {f['key']} \"{f['opening']}\"")
        else:
            lines.append(f"  {span(f)}: {f['length']} consecutive paragraphs open "
                         f"with the {f['key']} \"{f['opening']}\"")
    if not result["template_runs"]:
        lines.append("  (none)")
    lines.append("Caption-text overlap (word-for-word repetition?)")
    for f in result["caption_overlap"]:
        lines.append(f"  {f['label']} (caption L{f['caption_start']}) and paragraph "
                     f"{span(f)}: {f['length']} shared words: \"{f['shared']}\"")
    if not result["caption_overlap"]:
        lines.append("  (none)")
    if "references" in result:
        lines.append("Items referred to three times or more (is each repeat needed?)")
        for f in result["references"]:
            where = ", ".join(f"L{n}" for n in f["lines"])
            lines.append(f"  {f['label']}: {f['count']} times ({where})")
        if not result["references"]:
            lines.append("  (none)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    r"""Command-line entry point.

    Parameters
    ----------
    argv : list of str, optional
        Arguments; ``sys.argv[1:]`` if None.

    Returns
    -------
    int
        0 when the file was read, 2 when it could not be.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("file", help="LaTeX (.tex) or Markdown (.md) file")
    ap.add_argument("--registry", help="project-vocabulary.json; its multiword names are the phrases")
    ap.add_argument("--lines", help="report only findings that touch lines A-B")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap.add_argument("--min-repeats", type=int, default=3)
    ap.add_argument("--min-run", type=int, default=3)
    ap.add_argument("--min-overlap", type=int, default=8)
    ap.add_argument("--min-words", type=int, default=3,
                    help="fewest words of a registry name that is checked (default 3)")
    args = ap.parse_args(argv)
    path = Path(args.file)
    try:
        text = path.read_text()
    except OSError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    fmt = "markdown" if path.suffix.lower() in (".md", ".markdown") else "latex"
    reg = registry_phrases(Path(args.registry), args.min_words) if args.registry else []
    result = analyze(text, fmt, reg, args.min_repeats, args.min_run, args.min_overlap)
    if args.lines:
        a, _, b = args.lines.partition("-")
        result = restrict(result, int(a), int(b or a))
    if args.json:
        print(json.dumps(result, indent=1))
    else:
        print(f"Pattern report for {path} (advisory evidence for the reviewers, not verdicts)")
        print(format_report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
