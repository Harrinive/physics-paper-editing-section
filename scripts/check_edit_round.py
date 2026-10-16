#!/usr/bin/env python3
r"""Compliance gate for one round of the ``physics-paper-editing-section`` skill.

The skill is a long prose specification, and a run can drift from it without
anyone noticing.  This script turns the checkable part of the specification
into a command: a round may be reported as ``ready`` only when ``check`` exits
with code 0.  It implements the *reviewed* path and follows the disk layout of the skill::

    .physics-edit/<slug>/CURRENT
    .physics-edit/<slug>/runs/<round_id>/
        session.md  source-original.txt  source-boundaries.json
        candidate-snapshot.txt  section-brief.md  object-ledger.md
        manifest.json  completion-audit.md  reviews/  sentence-maps/

One round covers one file.  The text of the file is cut into *units* (one unit
per ``\item`` of a ``keypoints``, ``itemize`` or ``enumerate`` environment, one
per blank-line-separated block elsewhere) and the units are grouped into *chunks* of at most 12
sentences.  Comment lines are not part of the reviewed text: they are dropped
before hashing, so a changed source pointer does not make a review stale, but
any change of a sentence does.

Sub-commands
------------
``init``      create a round: copy the source, propose chunks, write templates.
``chunks``    print the chunks and write one sentence map per chunk.
``pending``   list, per chunk, the sentences that still lack a current PASS verdict.
``status``    one dashboard line per chunk: versions, pending, reviews, defects.
``prompt``    build a reviewer packet with an issued hash and print the launch line.
``digest``    print only the open findings of the recorded reports.
``rechunk``   re-cut the current text into chunks after bullets were split or merged.
``record``    write one review record (the hash is checked against the text); with
              ``--packet`` the hash, scope and keys come from the issued packet and
              the verdicts from the reviewer's JSON report.
``defect``    log or rule a defect of the author's source.
``revision``  bump the context or object-ledger revision (makes reviews stale).
``snapshot``  copy the live source to ``candidate-snapshot.txt``.
``gc``        list rounds past their retention; ``--compact`` drops the bulk of expired ones.
``check``     validate the round; exit 0 only when ``ready`` is allowed.

Scoped review
-------------
A sentence and a terminology review may cover the whole chunk (``--scope full``)
or only the sentences that lack a current verdict (``--scope touched``).  A
verdict belongs to a *sentence key*, the hash of the sentence together with the
sentence before it, so an edit invalidates the verdicts of the edited sentence
and of its successor and of nothing else, and a verdict survives a rechunk.
A chunk is accepted when every sentence has a current PASS verdict of both
roles and at least one full review of each role exists (the review at the close
of the chunk).

Exit codes of ``check``: 0 ready, 1 not ready (needs_fix or needs_user),
2 malformed round.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path


HARNESS_VERSION = 2
MAX_SENTENCES = 12
#: A chunk with more sentence or terminology reviews than this gets a note.
MAX_REVIEWS_BEFORE_NOTE = 8

AXES = (
    "scientific_fidelity",
    "physics_lead",
    "formal_validity",
    "terminology_notation",
    "prose",
)

#: Enumerations of ``session.md`` (skill: runtime-contract.md, disk-layout.md).
SESSION_ENUMS = {
    "round_status": {"active", "needs_user", "ready", "closed", "superseded"},
    "language_coverage": {"selective", "exhaustive"},
    "edit_intent": {"copyedit", "substantive"},
    "model_tier": {"strong", "economy", "unknown"},
    "tier_source": {"adapter", "user", "inherited", "fallback"},
    "scientific_risk": {"low", "medium", "high"},
    "review_profile": {"standard", "high_risk"},
    "formal_review_scope": {"none", "changed", "dependency_closure", "all_in_scope"},
    "role_model_policy": {"standing", "recommended", "parent", "custom", "pending"},
    "verification_independence": {"independent", "self_only", "unavailable"},
}

#: Facts the machine cannot see; the editor attests them in ``session.md``.
ATTESTATIONS = (
    "mapping_announced",
    "stage_b_convention_merge_done",
    "stage_b_parallel_template_done",
    "no_source_edit_boundary_audited",
    "checklist_walked",
)

#: Name of the project's role-to-model policy, at the repository root.  The skill
#: stores no default: when the file is absent the agent asks the owner and writes it
#: with ``policy set``.
POLICY_FILE = "physics-edit-policy.json"
#: Roles that have a policy entry; ``faithfulness_specialist`` is the principle
#: specialist for the principles in ``FAITHFULNESS_PRINCIPLES`` (physics faithfulness).
POLICY_ROLES = ("sentence_reviewer", "terminology_reviewer", "principle_specialist",
                "faithfulness_specialist", "holistic_reviewer", "formal_reviewer",
                "local_polisher")
#: Principles whose specialist runs under the ``faithfulness_specialist`` entry.
FAITHFULNESS_PRINCIPLES = {"P11"}
EFFORTS = ("low", "medium", "high", "xhigh", "max")

ROLES = (set(POLICY_ROLES) - {"faithfulness_specialist"}) | {"editor_closure"}


class PolicyMissing(Exception):
    """The project has no role-to-model policy file."""


def load_policy(root: Path) -> dict[str, tuple[str, str]]:
    r"""Read the role-to-model policy of the project.

    Parameters
    ----------
    root : Path
        Repository root; the policy is ``physics-edit-policy.json`` there.

    Returns
    -------
    dict
        ``{role: (model family, effort)}`` for every role in ``POLICY_ROLES``.

    Raises
    ------
    PolicyMissing
        If the file is absent or lacks a role.
    """
    path = root / POLICY_FILE
    if not path.exists():
        raise PolicyMissing(
            f"no role-to-model policy at {path}; ask the owner which model and effort each "
            f"reviewer role uses, then write it with `policy set` (see `policy --help`)")
    roles = json.loads(path.read_text()).get("roles", {})
    missing = [r for r in POLICY_ROLES if r not in roles]
    if missing:
        raise PolicyMissing(f"{path} has no entry for {missing}; complete it with `policy set`")
    return {r: (roles[r]["model"].lower(), roles[r]["effort"]) for r in POLICY_ROLES}


def role_policy(policy: dict[str, tuple[str, str]], role: str,
                principles: list[str] | tuple[str, ...] = ()) -> tuple[str, str]:
    r"""Model family and effort of a role.

    Parameters
    ----------
    policy : dict
        Output of :func:`load_policy`.
    role : str
        A reviewer role.
    principles : sequence of str, optional
        Principles of a specialist; any physics-faithfulness principle selects
        the ``faithfulness_specialist`` entry.

    Returns
    -------
    tuple of str
        ``(model family, effort)``.
    """
    if role == "principle_specialist" and set(principles) & FAITHFULNESS_PRINCIPLES:
        return policy["faithfulness_specialist"]
    return policy[role]


#: Principle groups of review-prompts.md ("Principle specialist" table).
PRINCIPLE_GROUPS = (
    {"P01", "P02"},
    {"P03", "P15"},
    {"P04", "P09", "P10"},
    {"P05", "P13"},
    {"P06", "P08", "P14"},
    {"P07"},
    {"P11"},
    {"P12"},
)

CANON = (
    "physics-paper-principles/SKILL.md",
    "physics-paper-principles/sentence.md",
    "physics-paper-principles/narrative.md",
    "physics-paper-principles/math.md",
    "physics-paper-principles/physical-lead.md",
)

STATUSES = {"PASS", "FIX", "USER_DECISION"}
AXIS_STATUSES = STATUSES | {"N/A"}

LIST_BEGIN_RE = re.compile(r"\\begin\{(keypoints|itemize|enumerate)\}")
LIST_END_RE = re.compile(r"\\end\{(keypoints|itemize|enumerate)\}")
HEADING_RE = re.compile(r"^\\(section|subsection|subsubsection|paragraph)\*?\{")
ABBREVIATIONS = (
    "Sec.", "Secs.", "Fig.", "Figs.", "Eq.", "Eqs.", "Ref.", "Refs.",
    "et al.", "i.e.", "e.g.", "vs.", "cf.", "No.",
)


# ---------------------------------------------------------------------------
# text handling
# ---------------------------------------------------------------------------

def strip_comment(line: str) -> str:
    r"""Remove a LaTeX comment from one line.

    Parameters
    ----------
    line : str
        One line of LaTeX source.

    Returns
    -------
    str
        The line up to the first unescaped ``%``, without trailing blanks.
    """
    for i, ch in enumerate(line):
        if ch == "%" and (i == 0 or line[i - 1] != "\\"):
            return line[:i].rstrip()
    return line.rstrip()


def normalized(lines: list[str]) -> str:
    r"""Reviewed form of some lines: no comments, no empty lines.

    Parameters
    ----------
    lines : list of str
        Raw source lines.

    Returns
    -------
    str
        The lines joined by newlines after dropping comments and empty lines.
    """
    kept = [strip_comment(line) for line in lines]
    return "\n".join(line for line in kept if line.strip())


def sha(text: str) -> str:
    r"""SHA-256 of a text.

    Parameters
    ----------
    text : str
        The text to hash.

    Returns
    -------
    str
        Hexadecimal digest of the UTF-8 encoding.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_sentences(text: str, raw: bool = False) -> list[str]:
    r"""Split reviewed LaTeX text into typographic sentences (heuristic).

    Displayed equations and inline math are replaced by a placeholder so that
    their punctuation does not split a sentence; common abbreviations and
    citations are protected.  The same function defines the sentence IDs of a
    chunk, so it only has to be deterministic, not perfect.

    Parameters
    ----------
    text : str
        Reviewed text (comments already removed).
    raw : bool, optional
        If True, return the same sentences with the original math, equations
        and references restored instead of the placeholders ``M``, ``EQ``,
        ``R``.  The split points are identical, so sentence ``k`` of the raw
        list is sentence ``k`` of the placeholder list.

    Returns
    -------
    list of str
        The sentences, each with at least two words.
    """
    store: list[str] = []

    def hide(tag: str):
        """Replacement function that stores the match and leaves ``tag``."""
        def repl(match: re.Match) -> str:
            if not raw:
                return f" {tag} "
            store.append(match.group(0))
            return f" {tag}\u27e6{len(store) - 1}\u27e7 "
        return repl

    t = re.sub(
        r"\\begin\{(equation|align|split|gather|multline|eqnarray)\*?\}.*?\\end\{\1\*?\}",
        hide("EQ"), text, flags=re.S)
    t = re.sub(r"\$\$.*?\$\$", hide("M"), t, flags=re.S)
    t = re.sub(r"(?<!\\)\$.*?(?<!\\)\$", hide("M"), t, flags=re.S)
    t = re.sub(r"\\item\b", " ", t)
    t = re.sub(r"\\(includegraphics|figpanel|hyperref)\*?(\[[^\]]*\])?(\{[^}]*\})+", hide("R"), t)
    t = re.sub(r"\\(cite|ref|eqref|label)\*?(\[[^\]]*\])?\{[^}]*\}", hide("R"), t)
    t = re.sub(r"\\(centering|small|footnotesize)\b", " ", t)
    t = t.replace("~", " ")
    for abbr in ABBREVIATIONS:
        t = t.replace(abbr, abbr.replace(".", "<DOT>"))
    t = re.sub(r"\b([A-Z])\.", r"\1<DOT>", t)
    parts = re.split(r"(?<=[.!?])[\"')\}]*\s+(?=[A-Z\\(\[])", t)
    out = []
    for part in parts:
        words = re.findall(r"[A-Za-z]{2,}", part.replace("<DOT>", "."))
        if len(words) >= 2:
            sentence = part.replace("<DOT>", ".").strip()
            if raw:
                sentence = re.sub(r"(?:EQ|M|R)\u27e6(\d+)\u27e7",
                                  lambda m: store[int(m.group(1))], sentence)
            out.append(sentence)
    return out


def split_units(lines: list[str]) -> list[dict]:
    r"""Cut a source file into units of reviewed text.

    A unit is one ``\item`` of a ``keypoints``, ``itemize`` or ``enumerate`` environment or one
    blank-line-separated block elsewhere (prose, caption, table).  Headings
    are not units; the first unit after a ``\section`` or ``\subsection`` is
    marked as a boundary where a new chunk must start.

    Parameters
    ----------
    lines : list of str
        Raw lines of the source file.

    Returns
    -------
    list of dict
        One dict per unit with keys ``kind``, ``start``, ``end`` (1-based
        inclusive line numbers), ``lines``, ``heading``, ``boundary``,
        ``text`` (reviewed form) and ``sentences``.
    """
    units: list[dict] = []
    state = {"cur": None, "heading": "", "boundary": False}

    def flush() -> None:
        """Close the open unit, if any."""
        cur = state["cur"]
        if cur is not None and cur["lines"]:
            units.append(cur)
        state["cur"] = None

    def open_unit(kind: str, no: int) -> dict:
        """Open a unit that starts at line ``no``."""
        unit = {"kind": kind, "start": no, "end": no, "lines": [],
                "heading": state["heading"], "boundary": state["boundary"]}
        state["boundary"] = False
        state["cur"] = unit
        return unit

    depth = 0
    for no, line in enumerate(lines, 1):
        s = line.strip()
        if LIST_BEGIN_RE.match(s):
            flush()
            depth += 1
            continue
        if LIST_END_RE.match(s):
            flush()
            depth = max(0, depth - 1)
            continue
        if depth:
            if s.startswith("\\item"):
                flush()
                open_unit("item", no)
            if state["cur"] is None:
                if s.startswith("%") or not s:
                    continue
                open_unit("item", no)
            state["cur"]["lines"].append(line)
            state["cur"]["end"] = no
            continue
        m = HEADING_RE.match(s)
        if m:
            flush()
            state["heading"] = s
            if m.group(1) != "paragraph":
                state["boundary"] = True
            continue
        if s.startswith("\\label{"):
            continue
        if not s:
            flush()
            continue
        if state["cur"] is None:
            if s.startswith("%"):
                continue
            open_unit("prose", no)
        state["cur"]["lines"].append(line)
        state["cur"]["end"] = no
    flush()
    for unit in units:
        unit["text"] = normalized(unit["lines"])
        unit["sentences"] = split_sentences(unit["text"])
        unit["raw_sentences"] = split_sentences(unit["text"], raw=True)
    return units


def propose_chunks(units: list[dict], first_id: int = 1) -> list[dict]:
    r"""Group consecutive units into chunks of at most 12 sentences.

    A new chunk starts at every ``\section``/``\subsection`` boundary and
    whenever the next unit would push the chunk over 12 sentences.  A single
    unit with more than 12 sentences becomes an oversized chunk of its own.

    Parameters
    ----------
    units : list of dict
        Output of :func:`split_units`.
    first_id : int, optional
        Number of the first chunk id (``c01`` for 1).

    Returns
    -------
    list of dict
        Chunks with ``id``, ``first_unit``, ``last_unit`` (1-based, inclusive),
        ``oversized`` and ``oversized_reason``.
    """
    chunks: list[dict] = []
    cur = None
    count = 0
    for idx, unit in enumerate(units, 1):
        n = len(unit["sentences"])
        start_new = (cur is None or unit["boundary"] or
                     (count > 0 and count + n > MAX_SENTENCES) or n > MAX_SENTENCES)
        if start_new:
            cur = {"id": f"c{first_id + len(chunks):02d}", "first_unit": idx,
                   "last_unit": idx, "oversized": False, "oversized_reason": ""}
            chunks.append(cur)
            count = 0
        cur["last_unit"] = idx
        count += n
        if count > MAX_SENTENCES:
            cur["oversized"] = True
            cur["oversized_reason"] = "TODO: name the indivisible definition or equation"
    return chunks


def chunk_text(units: list[dict], chunk: dict) -> str:
    r"""Reviewed text of one chunk.

    Parameters
    ----------
    units : list of dict
        Output of :func:`split_units`.
    chunk : dict
        A manifest chunk with ``first_unit`` and ``last_unit``.

    Returns
    -------
    str
        The reviewed text of the units of the chunk, joined by newlines.
    """
    sel = units[chunk["first_unit"] - 1:chunk["last_unit"]]
    return "\n".join(u["text"] for u in sel if u["text"])


def chunk_sentences(units: list[dict], chunk: dict) -> list[tuple[str, str]]:
    r"""Sentence IDs and sentences of one chunk.

    Parameters
    ----------
    units : list of dict
        Output of :func:`split_units`.
    chunk : dict
        A manifest chunk.

    Returns
    -------
    list of (str, str)
        ``("S01", sentence)`` pairs in reading order.
    """
    sel = units[chunk["first_unit"] - 1:chunk["last_unit"]]
    sentences = [s for u in sel for s in u["sentences"]]
    return [(f"S{i:02d}", s) for i, s in enumerate(sentences, 1)]


def chunk_keys(units: list[dict], chunk: dict) -> dict[str, str]:
    r"""Sentence keys of one chunk.

    The key of a sentence is the hash of the sentence and of the sentence
    before it (the last sentence of the preceding unit for the first sentence
    of a chunk).  A reference such as "this probability" depends on its
    antecedent, so the verdict on a sentence is only valid while both texts
    are unchanged.

    Parameters
    ----------
    units : list of dict
        Output of :func:`split_units`.
    chunk : dict
        A manifest chunk.

    Returns
    -------
    dict
        ``{"S01": key, ...}`` in reading order.
    """
    before = [s for u in units[:chunk["first_unit"] - 1] for s in u["sentences"]]
    previous = before[-1] if before else ""
    keys: dict[str, str] = {}
    for sid, sentence in chunk_sentences(units, chunk):
        keys[sid] = sha(previous + "\n" + sentence)
        previous = sentence
    return keys


# ---------------------------------------------------------------------------
# round state
# ---------------------------------------------------------------------------

def now() -> str:
    r"""Current UTC time as an ISO string.

    Returns
    -------
    str
        Time with microsecond resolution, ending in ``Z`` (records written in the
        same second must still sort in the order they were written).
    """
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def read_keys(path: Path) -> dict[str, str]:
    r"""Read top-level ``key: value`` lines of a markdown file.

    Parameters
    ----------
    path : Path
        File to read.

    Returns
    -------
    dict
        Key -> value; the value is cut at the first `` (`` or `` #``.
    """
    keys: dict[str, str] = {}
    for line in path.read_text().splitlines():
        m = re.match(r"^([a-z_][a-z0-9_]*):\s*(.*?)\s*$", line)
        if m and m.group(1) not in keys:
            value = re.split(r"\s+[(#]", m.group(2))[0].strip()
            keys[m.group(1)] = value
    return keys


def load_json(path: Path) -> dict:
    r"""Read a JSON file.

    Parameters
    ----------
    path : Path
        File to read.

    Returns
    -------
    dict
        The parsed object.
    """
    return json.loads(path.read_text())


def save_json(path: Path, data: dict) -> None:
    r"""Write a JSON file with stable formatting.

    Parameters
    ----------
    path : Path
        Target file.
    data : dict
        Object to store.
    """
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


class Round:
    r"""The files of one round and the text they refer to.

    Parameters
    ----------
    root : Path
        Repository root (the folder that holds ``.physics-edit``).
    folder : Path
        The round folder ``.physics-edit/<slug>/runs/<round_id>``.
    """

    def __init__(self, root: Path, folder: Path):
        """Remember the paths; nothing is read until :meth:`load`."""
        self.root = root
        self.folder = folder
        self.session: dict[str, str] = {}
        self.manifest: dict = {}
        self.units: list[dict] = []
        self.live_text = ""

    def load(self) -> None:
        r"""Read session, manifest, and the live source file.

        Raises
        ------
        FileNotFoundError
            If one of these files is missing.
        """
        self.session = read_keys(self.folder / "session.md")
        self.manifest = load_json(self.folder / "manifest.json")
        source = self.root / self.manifest["source_file"]
        self.live_text = source.read_text()
        self.units = split_units(self.live_text.splitlines())

    def role(self, role: str, principles: list[str] | tuple[str, ...] = ()) -> tuple[str, str]:
        r"""Model family and effort that the project policy assigns to a role.

        Parameters
        ----------
        role : str
            A reviewer role.
        principles : sequence of str, optional
            Principles of a specialist.

        Returns
        -------
        tuple of str
            ``(model family, effort)``.

        Raises
        ------
        PolicyMissing
            If the project has no complete policy file.
        """
        return role_policy(load_policy(self.root), role, principles)

    def has_closure(self, chunk: dict) -> bool:
        r"""Whether the editor closure of the current text of a chunk is recorded.

        Parameters
        ----------
        chunk : dict
            A manifest chunk.

        Returns
        -------
        bool
            True if an ``editor_closure`` record has the current chunk hash and
            the current context and ledger revisions.
        """
        man, text_hash = self.manifest, self.chunk_hash(chunk)
        return any(r.get("role") == "editor_closure" and r.get("chunk_id") == chunk["id"]
                   and r.get("snapshot_sha256") == text_hash
                   and r.get("context_revision") == man["context_revision"]
                   and r.get("ledger_revision") == man["ledger_revision"]
                   for r in self.reviews())

    def open_packets(self) -> list[dict]:
        r"""Packets that were issued but not yet recorded.

        Returns
        -------
        list of dict
            Packet metadata, oldest first.
        """
        folder = self.folder / "packets"
        if not folder.exists():
            return []
        done = {r.get("packet") for r in self.reviews() if r.get("packet")}
        metas = [load_json(p) for p in sorted(folder.glob("p*.json"))
                 if not p.name.endswith(".report.json")]
        return [m for m in metas if m["id"] not in done]

    def context_digest(self) -> str:
        r"""Hash of the files that a packet embeds besides the chunk.

        Returns
        -------
        str
            SHA-256 over the section brief, the object ledger and the reviewer context.
        """
        parts = [(self.folder / n).read_text() if (self.folder / n).exists() else ""
                 for n in ("section-brief.md", "object-ledger.md", "reviewer-context.md")]
        return sha("\n--\n".join(parts))

    def whole_hash(self) -> str:
        r"""Hash of the reviewed text of the whole live file.

        Returns
        -------
        str
            SHA-256 of the file after dropping comments and empty lines.
        """
        return sha(normalized(self.live_text.splitlines()))

    def chunk_hash(self, chunk: dict) -> str:
        r"""Hash of the reviewed text of one chunk.

        Parameters
        ----------
        chunk : dict
            A manifest chunk.

        Returns
        -------
        str
            SHA-256 of :func:`chunk_text`.
        """
        return sha(chunk_text(self.units, chunk))

    def chunk(self, chunk_id: str) -> dict | None:
        r"""Find a manifest chunk by id.

        Parameters
        ----------
        chunk_id : str
            Id such as ``c03``.

        Returns
        -------
        dict or None
            The chunk, or None if absent.
        """
        for chunk in self.manifest.get("chunks", []):
            if chunk["id"] == chunk_id:
                return chunk
        return None

    def coverage(self, role: str, chunk: dict) -> dict[str, tuple[str, dict]]:
        r"""Current verdict of a role on each sentence key of the live text.

        Records of the current context and ledger revision are read in
        creation order and the newest verdict of a key wins.  A record that
        predates sentence keys counts only for the whole chunk, and only while
        its snapshot equals the current text of the chunk.

        Parameters
        ----------
        role : str
            ``sentence_reviewer`` or ``terminology_reviewer``.
        chunk : dict
            A manifest chunk (used for the legacy fallback).

        Returns
        -------
        dict
            ``{key: (status, record)}`` for every key with a verdict.
        """
        man = self.manifest
        cur_keys = chunk_keys(self.units, chunk)
        text_hash = self.chunk_hash(chunk)
        out: dict[str, tuple[str, dict]] = {}
        for rec in self.reviews():
            waives = rec.get("role") == "editor_waiver" and role in rec.get("waives", [])
            if ((rec.get("role") != role and not waives)
                    or rec.get("context_revision") != man["context_revision"]
                    or rec.get("ledger_revision") != man["ledger_revision"]):
                continue
            if "sentence_keys" in rec:
                for sid, key in rec["sentence_keys"].items():
                    status = rec.get("sentence_results", {}).get(sid)
                    if status in STATUSES:
                        out[key] = (status, rec)
            elif rec.get("chunk_id") == chunk["id"] and rec.get("snapshot_sha256") == text_hash:
                if role == "sentence_reviewer":
                    results = rec.get("sentence_results", {})
                else:
                    status = rec.get("quality", {}).get("terminology_notation")
                    results = {sid: status for sid in cur_keys}
                for sid, key in cur_keys.items():
                    if results.get(sid) in STATUSES:
                        out[key] = (results[sid], rec)
        return out

    def pending(self, role: str, chunk: dict) -> list[str]:
        r"""Sentence ids of a chunk without a current PASS verdict of a role.

        Parameters
        ----------
        role : str
            ``sentence_reviewer`` or ``terminology_reviewer``.
        chunk : dict
            A manifest chunk.

        Returns
        -------
        list of str
            Sentence ids in reading order.
        """
        cov = self.coverage(role, chunk)
        return [sid for sid, key in chunk_keys(self.units, chunk).items()
                if cov.get(key, ("", {}))[0] != "PASS"]

    def reviews(self) -> list[dict]:
        r"""All review records of the round.

        Returns
        -------
        list of dict
            Parsed ``reviews/*.json`` files sorted by creation time.
        """
        out = []
        for path in sorted((self.folder / "reviews").glob("*.json")):
            rec = load_json(path)
            rec["_file"] = path.name
            out.append(rec)
        out.sort(key=lambda r: (r.get("created_at", ""), r["_file"]))
        return out


def find_round(root: Path, arg: str) -> Round:
    r"""Resolve a round argument to a :class:`Round`.

    Parameters
    ----------
    root : Path
        Repository root.
    arg : str
        Either a path to a round folder, or ``<slug>`` (the round named in
        ``.physics-edit/<slug>/CURRENT``).

    Returns
    -------
    Round
        The loaded round.
    """
    path = Path(arg)
    if not path.is_dir():
        current = root / ".physics-edit" / arg / "CURRENT"
        path = root / ".physics-edit" / arg / current.read_text().strip()
    rnd = Round(root, path.resolve())
    rnd.load()
    return rnd


# ---------------------------------------------------------------------------
# templates
# ---------------------------------------------------------------------------

SESSION_TEMPLATE = """# Session: {slug}, round {round_id}

harness_version: 2
round_id: {round_id}
round_status: active
created_at: {created}
source_file: {source_file}
language_coverage: {language_coverage}
edit_intent: {edit_intent}
model_tier: strong
tier_source: adapter
scientific_risk: {risk}
review_profile: {profile}
formal_review_scope: {scope}
formal_none_reason:
role_model_policy: standing
verification_independence: independent

# Attestations the machine cannot see (yes | no | n/a where stated).
mapping_announced: no
stage_b_convention_merge_done: no
stage_b_parallel_template_done: no
no_source_edit_boundary_audited: no
checklist_walked: no

# Role-to-model policy: physics-edit-policy.json at the repository root.
"""

BRIEF_TEMPLATE = """# Section brief
context_revision: ctx-1

## Physics spine
TODO: situation, mechanism, relevant quantities, principal result.

## Neighbouring context and conventions
TODO
"""

LEDGER_TEMPLATE = """# Object ledger
revision: L1

| Object | Category | Scope | Dimensions / scaling | Factors, normalization | First use | Payoff | Disposition |
|---|---|---|---|---|---|---|---|
| TODO | | | | | | | |
"""

AUDIT_TEMPLATE = """# Completion audit
Deviations from the skill: TODO (write "none" or list each deviation and why)
"""


# ---------------------------------------------------------------------------
# sub-commands
# ---------------------------------------------------------------------------

def root_of(args: argparse.Namespace) -> Path:
    r"""Repository root of a command.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed arguments (``root`` may be None).

    Returns
    -------
    Path
        ``--root`` if given, else the top level of the git repository that contains
        the current directory, else the current directory.
    """
    if args.root:
        return Path(args.root).resolve()
    import subprocess
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True, check=True).stdout.strip()
        return Path(top).resolve()
    except (OSError, subprocess.CalledProcessError):
        return Path.cwd().resolve()


def print_chunk_table(units: list[dict], chunks: list[dict]) -> None:
    r"""Print one line per chunk.

    Parameters
    ----------
    units : list of dict
        Output of :func:`split_units`.
    chunks : list of dict
        Manifest chunks.
    """
    total = 0
    for chunk in chunks:
        n = len(chunk_sentences(units, chunk))
        total += n
        first = units[chunk["first_unit"] - 1]
        last = units[chunk["last_unit"] - 1]
        flag = "  OVERSIZED" if n > MAX_SENTENCES else ""
        print(f"{chunk['id']}  units {chunk['first_unit']:>3}-{chunk['last_unit']:<3} "
              f"lines {first['start']:>4}-{last['end']:<4} sentences {n:>2}"
              f"  sha {sha(chunk_text(units, chunk))[:10]}{flag}")
    print(f"{len(chunks)} chunks, {total} sentences, {len(units)} units")


def cmd_init(args: argparse.Namespace) -> int:
    r"""Create a round (or show the chunk plan with ``--dry-run``).

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``init`` sub-command.

    Returns
    -------
    int
        Exit code.
    """
    root = root_of(args)
    source = (root / args.source).resolve()
    rel = str(source.relative_to(root))
    units = split_units(source.read_text().splitlines())
    chunks = propose_chunks(units)
    print_chunk_table(units, chunks)
    if args.dry_run:
        return 0
    load_policy(root)
    base = root / ".physics-edit" / args.slug / "runs"
    number = len(list(base.glob("r*-*"))) + 1 if base.exists() else 1
    round_id = args.round_id or f"r{number}-{dt.date.today().isoformat()}"
    folder = base / round_id
    folder.mkdir(parents=True)
    (folder / "reviews").mkdir()
    (folder / "sentence-maps").mkdir()
    original = folder / "source-original.txt"
    shutil.copy(source, original)
    original.chmod(0o444)
    shutil.copy(source, folder / "candidate-snapshot.txt")
    (root / ".physics-edit" / args.slug / "CURRENT").write_text(f"runs/{round_id}\n")
    (folder / "session.md").write_text(SESSION_TEMPLATE.format(
        slug=args.slug, round_id=round_id, source_file=rel, created=now(),
        language_coverage=args.coverage, edit_intent=args.intent,
        risk=args.risk, profile="high_risk" if args.risk == "high" else "standard",
        scope="all_in_scope" if args.risk == "high" else "dependency_closure"))
    (folder / "section-brief.md").write_text(BRIEF_TEMPLATE)
    (folder / "object-ledger.md").write_text(LEDGER_TEMPLATE)
    (folder / "completion-audit.md").write_text(AUDIT_TEMPLATE)
    save_json(folder / "source-boundaries.json", {
        "source_file": rel, "source_sha256": sha(source.read_text()),
        "units": [{"u": i, "kind": u["kind"], "start": u["start"], "end": u["end"],
                   "heading": u["heading"], "boundary": u["boundary"]}
                  for i, u in enumerate(units, 1)]})
    save_json(folder / "manifest.json", {
        "harness_version": HARNESS_VERSION, "round_id": round_id, "source_file": rel,
        "source_original_sha256": sha(source.read_text()),
        "context_revision": "ctx-1", "ledger_revision": "L1",
        "chunks": chunks, "source_defects": []})
    print(f"round created: {folder}")
    return 0


def cmd_chunks(args: argparse.Namespace) -> int:
    r"""Print the chunks of a round and write the sentence maps.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``chunks`` sub-command.

    Returns
    -------
    int
        Exit code.
    """
    rnd = find_round(root_of(args), args.round)
    print_chunk_table(rnd.units, rnd.manifest["chunks"])
    maps = rnd.folder / "sentence-maps"
    maps.mkdir(exist_ok=True)
    for chunk in rnd.manifest["chunks"]:
        lines = [f"# {chunk['id']}  sha256 {rnd.chunk_hash(chunk)}", ""]
        lines += [f"[{sid}] {text}" for sid, text in chunk_sentences(rnd.units, chunk)]
        (maps / f"{chunk['id']}.txt").write_text("\n".join(lines) + "\n")
    print(f"whole-text sha {rnd.whole_hash()[:10]}  (sentence maps in {maps})")
    return 0


def cmd_pending(args: argparse.Namespace) -> int:
    r"""Print, per chunk, the sentences that still lack a current PASS verdict.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``pending`` sub-command.

    Returns
    -------
    int
        Exit code (0 even when something is pending).
    """
    rnd = find_round(root_of(args), args.round)
    for chunk in rnd.manifest["chunks"]:
        sent = rnd.pending("sentence_reviewer", chunk)
        term = rnd.pending("terminology_reviewer", chunk)
        n = len(chunk_keys(rnd.units, chunk))
        print(f"{chunk['id']}  sentences {n:>2}  sentence review pending: "
              f"{','.join(sent) or '-'}  terminology pending: {','.join(term) or '-'}")
    return 0


def parse_pairs(text: str | None) -> dict[str, str]:
    r"""Parse ``A=B,C=D`` into a dict.

    Parameters
    ----------
    text : str or None
        Comma-separated ``key=value`` pairs.

    Returns
    -------
    dict
        Mapping; empty for None.
    """
    out: dict[str, str] = {}
    for item in (text or "").split(","):
        if item.strip():
            key, _, value = item.partition("=")
            out[key.strip()] = value.strip()
    return out


def cmd_rechunk(args: argparse.Namespace) -> int:
    r"""Cut the current text into new chunks (after bullets were split or merged).

    Drafting from a skeleton changes the number of units, so the chunks made
    at ``init`` no longer partition the text.  New chunks get new ids after
    the highest existing one, except that a chunk with at least half of its
    sentences already reviewed under an old chunk id keeps that id; reviews of
    superseded chunks stay as history.  Verdicts follow the sentences, not the
    chunk ids.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``rechunk`` sub-command.

    Returns
    -------
    int
        Exit code.
    """
    rnd = find_round(root_of(args), args.round)
    old = rnd.manifest["chunks"]
    numbers = [int(c["id"][1:]) for c in old if re.fullmatch(r"c\d+", c["id"])]
    chunks = propose_chunks(rnd.units, first_id=max(numbers, default=0) + 1)
    # A chunk that is mostly the same sentences as an old chunk keeps its id, so the
    # close reviews of the old chunk still count and a late split costs nothing.
    seen: dict[str, set[str]] = {}
    for rec in rnd.reviews():
        if rec.get("role") in ("sentence_reviewer", "terminology_reviewer") and rec.get("sentence_keys"):
            seen.setdefault(rec["chunk_id"], set()).update(rec["sentence_keys"].values())
    pairs = []
    for new in chunks:
        keys = set(chunk_keys(rnd.units, new).values())
        for old_chunk in old:
            overlap = len(keys & seen.get(old_chunk["id"], set()))
            if keys and overlap * 2 >= len(keys):
                pairs.append((overlap, new["id"], old_chunk["id"]))
    renamed, used_new, used_old = {}, set(), set()
    for overlap, new_id, old_id in sorted(pairs, reverse=True):
        if new_id not in used_new and old_id not in used_old:
            renamed[new_id] = old_id
            used_new.add(new_id)
            used_old.add(old_id)
    for new in chunks:
        new["id"] = renamed.get(new["id"], new["id"])
    rnd.manifest.setdefault("chunk_history", []).append(
        {"at": now(), "superseded": [c["id"] for c in old if c["id"] not in used_old],
         "kept": sorted(used_old)})
    rnd.manifest["chunks"] = chunks
    save_json(rnd.folder / "manifest.json", rnd.manifest)
    print_chunk_table(rnd.units, chunks)
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    r"""Write one review record after checking it against the text.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``record`` sub-command.

    Returns
    -------
    int
        Exit code (2 for a rejected record).
    """
    rnd = find_round(root_of(args), args.round)
    if args.packet:
        return record_from_packet(rnd, args)
    if not (args.chunk and args.role and args.snapshot):
        return fail("record needs --packet, or --chunk, --role and --snapshot")
    role = args.role
    if role not in ROLES:
        return fail(f"unknown role {role!r}; use one of {sorted(ROLES)}")
    section_roles = {"holistic_reviewer", "formal_reviewer"}
    if (args.chunk == "section") != (role in section_roles):
        return fail("holistic and formal reviews belong to the whole text (--chunk section); "
                    "every other role belongs to one chunk")
    for item in (args.principles or "").split(","):
        if item and not re.fullmatch(r"P(0[1-9]|1[0-5])", item):
            return fail(f"unknown principle {item!r}")
    for name, value in parse_pairs(args.hits).items():
        if not re.fullmatch(r"P(0[1-9]|1[0-5])", name) or value not in STATUSES:
            return fail(f"--hits needs Pxx=PASS|FIX|USER_DECISION, got {name}={value}")
    if args.chunk == "section":
        current, ids = rnd.whole_hash(), []
        unsettled = [f for f in evaluate(rnd)[0] if re.match(r"c\d+:", f)]
        if unsettled:
            return fail("Stage E reviews a settled text, but a chunk still has an open item: "
                        + "; ".join(unsettled[:4]))
    else:
        chunk = rnd.chunk(args.chunk)
        if chunk is None:
            return fail(f"no chunk {args.chunk!r} in the manifest")
        current = rnd.chunk_hash(chunk)
        ids = [sid for sid, _ in chunk_sentences(rnd.units, chunk)]
    if not current.startswith(args.snapshot.lower()) or len(args.snapshot) < 8:
        return fail(f"snapshot {args.snapshot} does not match the current text "
                    f"({current[:10]}); the text changed after the review was launched")
    rec = {"harness_version": HARNESS_VERSION, "round_id": rnd.folder.name,
           "chunk_id": args.chunk, "role": role, "snapshot_sha256": current,
           "context_revision": rnd.manifest["context_revision"],
           "ledger_revision": rnd.manifest["ledger_revision"],
           "canon": list(CANON), "created_at": now(), "summary": args.summary or "",
           "verification_independence": rnd.session.get("verification_independence", ""),
           "blind": bool(args.blind), "user_decisions": [
               x for x in (args.user_decisions or "").split(",") if x]}
    if role != "editor_closure":
        family, effort = rnd.role(role, (args.principles or "").split(","))
        if family not in (args.model or "").lower() or args.effort != effort:
            return fail(f"role {role} must run on {family}/{effort}, "
                        f"got {args.model}/{args.effort}")
        rec.update({"requested_model": args.model, "requested_effort": args.effort,
                    "resolved_model": args.resolved_model or "unknown"})
    if role == "principle_specialist":
        rec["principles"] = [p for p in (args.principles or "").split(",") if p]
        if not rec["principles"]:
            return fail("a principle specialist needs --principles")
    if role in ("sentence_reviewer", "terminology_reviewer"):
        if args.chunk == "section":
            return fail("the sentence and terminology reviews belong to a chunk")
        scope = args.scope or "full"
        keys = chunk_keys(rnd.units, chunk)
        if scope in ("full", "close"):
            covered = ids
        else:
            wanted = [x for x in (args.touched or "").split(",") if x]
            covered = wanted or rnd.pending(role, chunk)
            if not covered:
                return fail("nothing to review: every sentence has a current PASS verdict")
            unknown = set(covered) - set(ids)
            if unknown:
                return fail(f"sentence ids not in the chunk: {sorted(unknown)}")
        marks = parse_pairs(args.sentences)
        extra = set(marks) - set(covered)
        if extra:
            return fail(f"sentence ids not in the reviewed scope: {sorted(extra)}")
        axes = parse_pairs(args.axes)
        default = args.default_status or ""
        if role == "terminology_reviewer" and not default and not marks:
            default = axes.get("terminology_notation", "")
        results = {sid: marks.get(sid, default) for sid in covered}
        missing = [s for s, v in results.items() if v not in STATUSES]
        if missing:
            return fail(f"no verdict for {missing}; pass --sentences, --default-status"
                        + (" or --axes" if role == "terminology_reviewer" else ""))
        rec["scope"] = "full" if scope == "close" else scope
        if scope == "close":
            rec["close"] = True
        rec["sentence_results"] = results
        rec["sentence_keys"] = {sid: keys[sid] for sid in covered}
        if role == "sentence_reviewer":
            rec["principle_hits"] = parse_pairs(args.hits)
            rec["quality"] = {"prose": "PASS" if all(v == "PASS" for v in results.values())
                              else "FIX"}
        else:
            vals = set(results.values())
            status = ("USER_DECISION" if "USER_DECISION" in vals
                      else "FIX" if "FIX" in vals else "PASS")
            rec["quality"] = {"terminology_notation": status}
    if role in ("holistic_reviewer", "formal_reviewer"):
        rec["quality"] = parse_pairs(args.axes)
        bad = {k: v for k, v in rec["quality"].items()
               if k not in AXES or v not in AXIS_STATUSES}
        if bad or not rec["quality"]:
            return fail(f"--axes needs axis=STATUS pairs; got {bad or 'nothing'}")
    if role == "formal_reviewer":
        rec["formal_review_scope"] = args.formal_scope or ""
    for dec in rec["user_decisions"]:
        if dec not in {d["id"] for d in rnd.manifest.get("source_defects", [])}:
            return fail(f"user decision {dec} is not logged; run `defect add` first")
    folder = rnd.folder / "reviews"
    folder.mkdir(exist_ok=True)
    tag = (args.principles or "").replace(",", "+")
    stem = f"{args.chunk}-{role}{('-' + tag) if tag else ''}"
    k = len(list(folder.glob(stem + "-*.json"))) + 1
    name = f"{stem}-{k}.json"
    if args.report:
        raw = folder / "raw"
        raw.mkdir(exist_ok=True)
        shutil.copy(args.report, raw / name.replace(".json", ".md"))
        rec["report"] = f"raw/{name.replace('.json', '.md')}"
    save_json(folder / name, rec)
    print(f"recorded {name} (snapshot {current[:10]})")
    return 0


# ---------------------------------------------------------------------------
# packets: prompt, record --packet, status, digest
# ---------------------------------------------------------------------------

MATH_RE = re.compile(
    r"\$\$.*?\$\$|(?<!\\)\$.*?(?<!\\)\$"
    r"|\\begin\{(?:equation|align|split|gather|multline|eqnarray)\*?\}.*?"
    r"\\end\{(?:equation|align|split|gather|multline|eqnarray)\*?\}",
    re.S)


def plain_text(raw: str) -> str:
    r"""Prose of a raw sentence: no math, no references, no markup braces.

    Parameters
    ----------
    raw : str
        A raw sentence.

    Returns
    -------
    str
        The sentence with math and references replaced by a space and
        ``\emph``/``\textit`` unwrapped.
    """
    t = MATH_RE.sub(" ", raw)
    t = re.sub(r"\\(?:cite|citep|citet|ref|eqref|autoref|cref|Cref)\*?(?:\[[^\]]*\])*\{[^}]*\}", " ", t)
    t = re.sub(r"\\label\{[^}]*\}", " ", t)
    t = re.sub(r"\\(?:emph|textit|textbf|text)\{([^{}]*)\}", r"\1", t)
    t = t.replace("~", " ")
    return re.sub(r"\s+", " ", t).strip()


def load_registry_terms(root: Path) -> list[dict]:
    r"""Terms of the project registry.

    Parameters
    ----------
    root : Path
        Repository root; the registry is ``project-vocabulary.json`` there.

    Returns
    -------
    list of dict
        The registry entries, or an empty list when the file is absent.
    """
    path = root / "project-vocabulary.json"
    if not path.exists():
        return []
    return json.loads(path.read_text()).get("terms", [])


PROMPT_FILE_CANDIDATES = (
    str(Path(__file__).resolve().parents[2] / "physics-paper-editing" / "review-prompts.md"),
    "~/.agents/skills/physics-paper-editing/review-prompts.md",
    "~/.claude/skills/physics-paper-editing/review-prompts.md",
)
ROLE_ALIASES = {"sentence": "sentence_reviewer", "terminology": "terminology_reviewer",
                "specialist": "principle_specialist"}
ROLE_HEADINGS = {"sentence_reviewer": "Sentence reviewer",
                 "terminology_reviewer": "Terminology-and-notation reviewer",
                 "principle_specialist": "Principle specialist"}
#: Canon files each packet role must read (names inside ``physics-paper-principles``).
ROLE_CANON = {"sentence_reviewer": ("SKILL.md", "sentence.md"),
              "terminology_reviewer": ("SKILL.md", "sentence.md", "physical-lead.md"),
              "principle_specialist": ("SKILL.md", "sentence.md")}
SPECIALIST_EXTRA_CANON = {"P05": "narrative.md", "P13": "narrative.md", "P07": "narrative.md",
                          "P11": "physical-lead.md", "P12": "math.md"}
REPORT_SCHEMA = """\
Write your report as one JSON file (UTF-8) at REPORT_PATH, and nowhere else.
Do not edit the manuscript or any other file.

{
  "packet": "PACKET_ID",
  "sentence_results": {"S03": "FIX", "S04": "PASS"},   // sentence and terminology roles:
                                                      // one entry per sentence in SCOPE
  "terminology_notation": "PASS | FIX | USER_DECISION", // terminology role only
  "principle_hits": {"P01": "FIX"},                    // sentence role: P01..P15
  "findings": [
    {"sentence": "S03", "principle": "P01", "severity": "must | optional",
     "evidence": "one or two sentences", "repair": "exact proposed wording"}
  ],
  "summary": "one line"
}
Use only PASS, FIX, USER_DECISION as verdicts. A finding of severity "optional"
never needs a repair; when every finding on a sentence is optional, the verdict of
that sentence is PASS. A specialist returns "findings" and "summary" only."""


def find_prompts(arg: str | None) -> Path:
    r"""Locate ``review-prompts.md`` of the ``physics-paper-editing`` skill.

    Parameters
    ----------
    arg : str or None
        Explicit path (``--prompts``); otherwise ``$EDIT_PROMPTS`` and the
        default skill folders are tried.

    Returns
    -------
    Path
        The file.

    Raises
    ------
    FileNotFoundError
        If none of the candidates exists.
    """
    import os
    for raw in (arg, os.environ.get("EDIT_PROMPTS"), *PROMPT_FILE_CANDIDATES):
        if raw and Path(raw).expanduser().is_file():
            return Path(raw).expanduser().resolve()
    raise FileNotFoundError("review-prompts.md not found; pass --prompts or set $EDIT_PROMPTS")


def role_prompt(path: Path, role: str) -> str:
    r"""Prompt text of a role: the first fenced block under its heading.

    Parameters
    ----------
    path : Path
        ``review-prompts.md``.
    role : str
        ``sentence_reviewer``, ``terminology_reviewer``, or ``principle_specialist``.

    Returns
    -------
    str
        The prompt block without the fence.
    """
    text = path.read_text()
    m = re.search(rf"^## {re.escape(ROLE_HEADINGS[role])}\s*$", text, re.M)
    if not m:
        raise ValueError(f"no heading '{ROLE_HEADINGS[role]}' in {path}")
    block = re.search(r"```text\n(.*?)\n```", text[m.end():], re.S)
    if not block:
        raise ValueError(f"no fenced prompt under '{ROLE_HEADINGS[role]}' in {path}")
    return block.group(1)


def ledger_rows(ledger: str, text: str) -> str:
    r"""Rows of the object ledger whose object occurs in a text.

    Parameters
    ----------
    ledger : str
        Content of ``object-ledger.md``.
    text : str
        Text of the chunk with its context.

    Returns
    -------
    str
        The table header and the matching rows; the whole ledger when it is
        not a table or nothing matches.
    """
    lines = ledger.splitlines()
    table = [ln for ln in lines if ln.strip().startswith("|")]
    if len(table) < 3:
        return ledger
    low = text.lower()
    head, body = table[:2], table[2:]
    keep = []
    for row in body:
        cell = row.strip().strip("|").split("|")[0]
        phrases = [x.strip(" `$") for x in re.split(r"[/;,]|\sand\s", cell)]
        phrases += re.findall(r"\\[A-Za-z]+", cell)
        if any(len(p) >= 3 and (p.lower() in low) for p in phrases if p):
            keep.append(row)
    if not keep:
        return ledger
    omitted = len(body) - len(keep)
    return "\n".join(head + keep) + (
        f"\n\n({omitted} further rows are in object-ledger.md; read it if a name is not here.)"
        if omitted else "")


def registry_entries(terms: list[dict], text: str) -> str:
    r"""Registry entries whose allowed or avoided name occurs in a text.

    Parameters
    ----------
    terms : list of dict
        Entries of ``project-vocabulary.json``.
    text : str
        Prose of the chunk with its context.

    Returns
    -------
    str
        One block per entry: term, meaning, allowed and avoided names.
    """
    low = text.lower()
    out = []
    for e in terms:
        names = (e.get("allowed_names") or [e["term"]]) + (e.get("avoid_names") or [])
        if any(re.search(rf"(?<![\w-]){re.escape(n.lower())}(?![\w-])", low) for n in names):
            out.append(f"- term: {e['term']}\n  meaning: {e.get('standard_meaning', '')}\n"
                       f"  allowed: {', '.join(e.get('allowed_names') or [e['term']])}\n"
                       f"  avoid: {', '.join(e.get('avoid_names') or []) or '-'}")
    return "\n".join(out) or "(no registry term occurs in this chunk)"


def issue_packet(rnd: Round, chunk: dict, role: str, scope: str, covered: list[str],
                 principles: list[str], prompts: Path) -> dict:
    r"""Write a reviewer packet and its metadata; return the metadata.

    Parameters
    ----------
    rnd : Round
        A loaded round.
    chunk : dict
        The chunk to review.
    role : str
        Reviewer role.
    scope : str
        ``full`` or ``touched``.
    covered : list of str
        Sentence ids the reviewer must give a verdict.
    principles : list of str
        Principle ids of a specialist.
    prompts : Path
        ``review-prompts.md``.

    Returns
    -------
    dict
        Packet metadata; the packet file and its report path are inside.
    """
    folder = rnd.folder / "packets"
    folder.mkdir(exist_ok=True)
    number = len(list(folder.glob("p*.json"))) + 1
    pid = f"p{number:03d}"
    keys = chunk_keys(rnd.units, chunk)
    sentences = chunk_sentences(rnd.units, chunk)
    raw = [s for u in rnd.units[chunk["first_unit"] - 1:chunk["last_unit"]]
           for s in u.get("raw_sentences", [])]
    if len(raw) != len(sentences):
        raw = [t for _, t in sentences]
    before = [s for u in rnd.units[:chunk["first_unit"] - 1][-1:] for s in u.get("raw_sentences", [])][-2:]
    after = [s for u in rnd.units[chunk["last_unit"]:][:1] for s in u.get("raw_sentences", [])][:2]
    chunk_prose = "\n".join(raw + before + after)
    plain = "\n".join(plain_text(x) for x in raw + before + after)

    skill_root = prompts.parent.parent / "physics-paper-principles"
    names = list(ROLE_CANON[role])
    if role == "principle_specialist":
        names += [SPECIALIST_EXTRA_CANON[p] for p in principles if p in SPECIALIST_EXTRA_CANON]
    canon = [str(skill_root / n) for n in dict.fromkeys(names)]
    prompt = role_prompt(prompts, role).replace("PRINCIPLE_IDS", ",".join(principles))

    brief = (rnd.folder / "section-brief.md").read_text()
    context_file = rnd.folder / "reviewer-context.md"
    terms = load_registry_terms(rnd.root)
    report = folder / f"{pid}.report.json"

    lines = [f"# Review packet {pid}", "",
             f"round {rnd.folder.name}; chunk {chunk['id']}; role {role}; "
             f"chunk text sha256 {rnd.chunk_hash(chunk)[:12]}; "
             f"context {rnd.manifest['context_revision']}, ledger {rnd.manifest['ledger_revision']}",
             "", "## Task", "", prompt, "",
             "## Canon (read before reviewing)", ""] + [f"- {c}" for c in canon] + [
             "", "## Scope", "",
             f"SCOPE = {scope}: " + ", ".join(covered) if role != "principle_specialist"
             else "SCOPE = the whole chunk (a specialist sweeps the whole unit)",
             "Sentences marked [scope] are yours to judge; all others, and the text before and "
             "after the chunk, are read-only context.", "",
             "## Report", "", REPORT_SCHEMA.replace("REPORT_PATH", str(report))
             .replace("PACKET_ID", pid), "", "## Candidate", "",
             "### Text before the chunk (context only)", ""] + (before or ["(none)"]) + [
             "", f"### Chunk {chunk['id']}", ""]
    for (sid, _), text in zip(sentences, raw):
        mark = "[scope] " if (role == "principle_specialist" or sid in covered) else ""
        lines.append(f"[{sid}] {mark}{text}")
    lines += ["", "### Text after the chunk (context only)", ""] + (after or ["(none)"])
    lines += ["", "## Section brief", "", brief]
    if context_file.exists():
        lines += ["", "## Reviewer context (rulings of the owner and conventions)", "",
                  context_file.read_text()]
    lines += ["", "## Object-ledger rows that occur in this chunk", "",
              ledger_rows((rnd.folder / "object-ledger.md").read_text(), chunk_prose), "",
              "## Registry entries that occur in this chunk", "",
              registry_entries(terms, plain)]
    path = folder / f"{pid}.md"
    path.write_text("\n".join(lines) + "\n")
    family, effort = rnd.role(role, principles)
    meta = {"id": pid, "role": role, "chunk_id": chunk["id"], "scope": scope,
            "covered_ids": covered, "principles": principles,
            "snapshot_sha256": rnd.chunk_hash(chunk), "sentence_keys": keys,
            "context_revision": rnd.manifest["context_revision"],
            "ledger_revision": rnd.manifest["ledger_revision"],
            "model": family, "effort": effort, "created_at": now(),
            "context_digest": rnd.context_digest(),
            "packet_file": str(path), "report_file": str(report)}
    save_json(folder / f"{pid}.json", meta)
    return meta


def cmd_prompt(args: argparse.Namespace) -> int:
    r"""Build a reviewer packet and print how to launch and record it.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``prompt`` sub-command.

    Returns
    -------
    int
        Exit code.
    """
    rnd = find_round(root_of(args), args.round)
    role = ROLE_ALIASES.get(args.role, args.role)
    if role not in ROLE_HEADINGS:
        return fail(f"role must be one of {sorted(ROLE_ALIASES)}")
    chunk = rnd.chunk(args.chunk)
    if chunk is None:
        return fail(f"no chunk {args.chunk!r} in the manifest")
    principles = [p for p in (args.principles or "").split(",") if p]
    if role == "principle_specialist" and not principles:
        return fail("a specialist packet needs --principles")
    ids = [sid for sid, _ in chunk_sentences(rnd.units, chunk)]
    if not rnd.has_closure(chunk):
        return fail(f"no editor closure for the current text of {chunk['id']}; run the editor's "
                    f"canon check, then `record --chunk {chunk['id']} --role editor_closure "
                    f"--snapshot {rnd.chunk_hash(chunk)[:12]} --summary ...`")
    if role == "principle_specialist":
        scope, covered = "full", ids
    else:
        pending = rnd.pending(role, chunk)
        has_full = any(r.get("chunk_id") == chunk["id"] and r.get("role") == role
                       and r.get("scope", "full") == "full" for r in rnd.reviews())
        scope = args.scope or ("full" if not has_full else ("touched" if pending else "close"))
        if scope == "close" and pending:
            return fail(f"a close review is issued when nothing is pending; pending: {','.join(pending)}")
        if scope in ("full", "close"):
            covered = ids
        else:
            explicit = [x for x in (args.touched or "").split(",") if x]
            covered = explicit or pending
            if not covered:
                return fail("nothing to review: every sentence has a current PASS verdict "
                            "(use --scope close for the review at the close of the chunk)")
            if not explicit:
                cov = rnd.coverage(role, chunk)
                keys = chunk_keys(rnd.units, chunk)
                unrepaired = [sid for sid in covered
                              if cov.get(keys[sid], ("", {}))[0] in ("FIX", "USER_DECISION")]
                if unrepaired:
                    return fail(f"{','.join(unrepaired)} still carry the verdict of the text they were "
                                "reviewed at; apply the finding, or record your decision with "
                                "`waive`, before reviewing again")
    try:
        prompts = find_prompts(args.prompts)
        meta = issue_packet(rnd, chunk, role, scope, covered, principles, prompts)
    except (FileNotFoundError, ValueError) as err:
        return fail(str(err))
    print(f"packet {meta['id']}: {role}, {chunk['id']}, scope {scope}"
          + (f" ({','.join(covered)})" if scope == "touched" else "")
          + f", chunk text {meta['snapshot_sha256'][:10]}")
    print(f"launch with model {meta['model']}, effort {meta['effort']}:")
    print(f"  Read {meta['packet_file']} and carry out the instructions in it exactly. "
          "That file is your full task.")
    print("record afterwards with:")
    print(f"  python3 {Path(__file__).resolve()} record {rnd.folder} --packet {meta['id']} "
          f"--report {meta['report_file']} --model {meta['model']} --effort {meta['effort']}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    r"""Print one dashboard line per chunk and the state of the whole round.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``status`` sub-command.

    Returns
    -------
    int
        Exit code.
    """
    rnd = find_round(root_of(args), args.round)
    records = rnd.reviews()
    man = rnd.manifest
    print(f"round {rnd.folder.name}  status {rnd.session.get('round_status')}  "
          f"context {man['context_revision']}  ledger {man['ledger_revision']}  "
          f"text {rnd.whole_hash()[:10]}")
    open_packets = rnd.open_packets()
    print(f"{'chunk':6}{'sent':>5}{'vers':>6}{'sent.rev':>9}{'term.rev':>9}{'spec':>6}"
          f"{'close s/t':>10}  pending sentence | terminology")
    for chunk in man["chunks"]:
        mine = [r for r in records if r.get("chunk_id") == chunk["id"]]
        by = lambda role: [r for r in mine if r.get("role") == role]  # noqa: E731
        versions = len({r.get("snapshot_sha256") for r in mine})
        ps, pt = rnd.pending("sentence_reviewer", chunk), rnd.pending("terminology_reviewer", chunk)
        n = len(chunk_keys(rnd.units, chunk))
        full = [("Y" if any(r.get("close") or "scope" not in r for r in by(role)) else "n")
                for role in ("sentence_reviewer", "terminology_reviewer")]
        out = [m["id"] for m in open_packets if m["chunk_id"] == chunk["id"]]
        print(f"{chunk['id']:6}{n:>5}{versions:>6}{len(by('sentence_reviewer')):>9}"
              f"{len(by('terminology_reviewer')):>9}{len(by('principle_specialist')):>6}"
              f"{'/'.join(full):>10}  {','.join(ps) or '-'} | {','.join(pt) or '-'}"
              + (f"  [packets out: {','.join(out)}]" if out else ""))
    sec = [r for r in records if r.get("chunk_id") == "section"]
    cur = [r for r in sec if r.get("snapshot_sha256") == rnd.whole_hash()
           and r.get("context_revision") == man["context_revision"]
           and r.get("ledger_revision") == man["ledger_revision"]]
    print(f"stage E: {len(sec)} section reviews, {len(cur)} on the current text")
    waivers = [r for r in records if r.get("role") == "editor_waiver"]
    print(f"packets out: {len(open_packets)}; waivers: {len(waivers)}")
    open_defects = [d["id"] for d in man.get("source_defects", []) if d["status"] != "ruled"]
    print(f"open defects: {', '.join(open_defects) or '-'}")
    last = max((r.get("created_at", "") for r in records), default="-")
    print(f"last record: {last}")
    return 0


def cmd_digest(args: argparse.Namespace) -> int:
    r"""Print the open findings of the recorded reports.

    A finding is open while the sentence it refers to still has the key that
    the reviewer saw and no newer verdict of the same role passed it.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``digest`` sub-command.

    Returns
    -------
    int
        Exit code.
    """
    rnd = find_round(root_of(args), args.round)
    man = rnd.manifest
    records = [r for r in rnd.reviews()
               if r.get("findings") and r.get("context_revision") == man["context_revision"]
               and r.get("ledger_revision") == man["ledger_revision"]]
    shown = 0
    for chunk in man["chunks"]:
        if args.chunk and chunk["id"] != args.chunk:
            continue
        current = {key: sid for sid, key in chunk_keys(rnd.units, chunk).items()}
        cov = {role: rnd.coverage(role, chunk)
               for role in ("sentence_reviewer", "terminology_reviewer")}
        rows = []
        for rec in records:
            if args.packet and rec.get("packet") != args.packet:
                continue
            for f in rec["findings"]:
                key = (rec.get("finding_sentence_keys", {}).get(f.get("sentence"))
                       or rec.get("sentence_keys", {}).get(f.get("sentence")))
                if key not in current:
                    continue
                newest = cov.get(rec["role"], {}).get(key)
                if newest is not None and newest[0] == "PASS" \
                        and newest[1].get("_file") != rec.get("_file") \
                        and newest[1].get("created_at", "") > rec.get("created_at", ""):
                    continue
                rows.append((current[key], rec["role"], f))
        if not rows:
            continue
        print(f"{chunk['id']}:")
        for sid, role, f in sorted(rows, key=lambda r: (r[2].get("severity") != "must", r[0])):
            tag = f"{role.split('_')[0]}"
            print(f"  {sid} {tag:<11} {f.get('principle', '-'):<4} {f.get('severity', '?'):<8} "
                  f"{(f.get('evidence') or '')[:150]}")
            if f.get("repair"):
                print(f"      repair: {f['repair'][:220]}")
            shown += 1
    print(f"{shown} open findings")
    return 0


def record_from_packet(rnd: Round, args: argparse.Namespace) -> int:
    r"""Write a review record from an issued packet and a JSON report.

    The text may have changed since the packet was issued: the record keeps
    the sentence keys of the packet, so verdicts on sentences that changed in
    the meantime simply no longer match the live text.

    Parameters
    ----------
    rnd : Round
        A loaded round.
    args : argparse.Namespace
        Arguments of ``record`` with ``--packet`` and ``--report``.

    Returns
    -------
    int
        Exit code (2 for a rejected record).
    """
    meta_path = rnd.folder / "packets" / f"{args.packet}.json"
    if not meta_path.exists():
        return fail(f"no packet {args.packet!r} in this round")
    meta = load_json(meta_path)
    role = meta["role"]
    if not args.report or not Path(args.report).exists():
        return fail("--report must name the reviewer's JSON report file")
    try:
        report = json.loads(Path(args.report).read_text())
    except json.JSONDecodeError as err:
        return fail(f"the report is not valid JSON: {err}")
    if report.get("packet") != meta["id"]:
        return fail(f"the report belongs to packet {report.get('packet')!r}, not {meta['id']!r}")
    family, effort = rnd.role(role, meta["principles"])
    if family not in (args.model or "").lower() or args.effort != effort:
        return fail(f"role {role} must run on {family}/{effort}, got {args.model}/{args.effort}")
    if (meta["context_revision"], meta["ledger_revision"]) != (
            rnd.manifest["context_revision"], rnd.manifest["ledger_revision"]):
        return fail("the context or ledger revision changed after the packet was issued; "
                    "issue a new packet")
    findings = report.get("findings", [])
    for f in findings:
        if f.get("sentence") not in meta["sentence_keys"]:
            return fail(f"finding for unknown sentence {f.get('sentence')!r}")
    rec = {"harness_version": HARNESS_VERSION, "round_id": rnd.folder.name,
           "chunk_id": meta["chunk_id"], "role": role, "packet": meta["id"],
           "snapshot_sha256": meta["snapshot_sha256"],
           "context_revision": meta["context_revision"],
           "ledger_revision": meta["ledger_revision"], "canon": list(CANON),
           "created_at": now(), "summary": report.get("summary", ""),
           "verification_independence": rnd.session.get("verification_independence", ""),
           "blind": False, "user_decisions": [], "requested_model": args.model,
           "requested_effort": args.effort, "resolved_model": args.resolved_model or "unknown",
           "findings": findings, "sentence_keys": meta["sentence_keys"]}
    if role == "principle_specialist":
        rec["principles"] = meta["principles"]
    else:
        covered = meta["covered_ids"]
        results = report.get("sentence_results", {})
        missing = [s for s in covered if results.get(s) not in STATUSES]
        extra = [s for s in results if s not in covered]
        if missing:
            return fail(f"no verdict for {missing}")
        if extra:
            return fail(f"sentence ids outside the packet scope: {extra}")
        rec["scope"] = "full" if meta["scope"] == "close" else meta["scope"]
        if meta["scope"] == "close":
            rec["close"] = True
        rec["sentence_results"] = {s: results[s] for s in covered}
        rec["sentence_keys"] = {s: meta["sentence_keys"][s] for s in covered}
        # findings may name context sentences of the chunk: keep their keys too
        rec["finding_sentence_keys"] = {f["sentence"]: meta["sentence_keys"][f["sentence"]]
                                        for f in findings}
        if role == "sentence_reviewer":
            hits = report.get("principle_hits", {})
            bad = {k: v for k, v in hits.items()
                   if not re.fullmatch(r"P(0[1-9]|1[0-5])", k) or v not in STATUSES}
            if bad:
                return fail(f"bad principle_hits {bad}")
            rec["principle_hits"] = hits
            rec["quality"] = {"prose": "PASS" if all(
                v == "PASS" for v in rec["sentence_results"].values()) else "FIX"}
        else:
            vals = set(rec["sentence_results"].values())
            status = ("USER_DECISION" if "USER_DECISION" in vals
                      else "FIX" if "FIX" in vals else "PASS")
            declared = report.get("terminology_notation")
            if declared in STATUSES and declared != status:
                return fail(f"terminology_notation {declared} contradicts the sentence verdicts")
            rec["quality"] = {"terminology_notation": status}
    folder = rnd.folder / "reviews"
    folder.mkdir(exist_ok=True)
    stem = f"{meta['chunk_id']}-{role}-{meta['id']}"
    raw = folder / "raw"
    raw.mkdir(exist_ok=True)
    shutil.copy(args.report, raw / f"{stem}.json")
    rec["report"] = f"raw/{stem}.json"
    save_json(folder / f"{stem}.json", rec)
    now_chunk = rnd.chunk(meta["chunk_id"])
    live = set(chunk_keys(rnd.units, now_chunk).values()) if now_chunk else set()
    stale = [s for s, k in rec.get("sentence_keys", {}).items() if k not in live]
    print(f"recorded {stem}.json from packet {meta['id']}"
          + (f"; {len(stale)} reviewed sentences changed since the packet was issued" if stale else ""))
    if meta.get("context_digest") and meta["context_digest"] != rnd.context_digest():
        print("warning: the section brief, the object ledger or the reviewer context changed after "
              "the packet was issued; bump the revision if the change matters")
    return 0


def cmd_policy(args: argparse.Namespace) -> int:
    r"""Show or write the role-to-model policy of the project.

    The skill stores no default policy.  The agent asks the owner which model
    and effort each reviewer role uses and records the answer here, once per
    project.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``policy`` sub-command.

    Returns
    -------
    int
        Exit code.
    """
    root = root_of(args)
    path = root / POLICY_FILE
    if args.action == "show":
        try:
            for role, (family, effort) in load_policy(root).items():
                print(f"{role:26} {family}/{effort}")
        except PolicyMissing as err:
            return fail(str(err))
        return 0
    roles = json.loads(path.read_text()).get("roles", {}) if path.exists() else {}
    for role in POLICY_ROLES:
        value = getattr(args, role)
        if value:
            model, _, effort = value.partition("/")
            if not model or effort not in EFFORTS:
                return fail(f"--{role.replace('_', '-')} needs MODEL/EFFORT with effort in {EFFORTS}")
            roles[role] = {"model": model.lower(), "effort": effort}
    missing = [r for r in POLICY_ROLES if r not in roles]
    if missing:
        return fail(f"the policy still lacks {missing}; give every role (MODEL/EFFORT)")
    path.write_text(json.dumps({"version": 1, "roles": roles}, indent=2) + "\n")
    print(f"policy written to {path}")
    return 0


def cmd_waive(args: argparse.Namespace) -> int:
    r"""Record the editor's decision not to apply a finding.

    A reviewer's FIX verdict on a sentence stays open until the sentence is
    changed and passes a review.  When the editor, after reading the finding,
    decides the sentence is right as written, the decision is recorded here
    with its reason; the sentence then counts as passed for the named roles.
    Waivers are listed by ``status`` and are part of the report to the owner.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``waive`` sub-command.

    Returns
    -------
    int
        Exit code.
    """
    rnd = find_round(root_of(args), args.round)
    chunk = rnd.chunk(args.chunk)
    if chunk is None:
        return fail(f"no chunk {args.chunk!r} in the manifest")
    if not (args.reason or "").strip():
        return fail("a waiver needs --reason: why the sentence is right as written")
    roles = [ROLE_ALIASES.get(x, x) for x in (args.roles or "sentence").split(",") if x]
    if not set(roles) <= {"sentence_reviewer", "terminology_reviewer"}:
        return fail("--roles takes sentence and/or terminology")
    keys = chunk_keys(rnd.units, chunk)
    ids = [x for x in args.sentences.split(",") if x]
    unknown = [x for x in ids if x not in keys]
    if unknown:
        return fail(f"sentence ids not in the chunk: {unknown}")
    folder = rnd.folder / "reviews"
    number = len(list(folder.glob(f"{chunk['id']}-editor_waiver-*.json"))) + 1
    rec = {"harness_version": HARNESS_VERSION, "round_id": rnd.folder.name,
           "chunk_id": chunk["id"], "role": "editor_waiver", "waives": roles,
           "snapshot_sha256": rnd.chunk_hash(chunk),
           "context_revision": rnd.manifest["context_revision"],
           "ledger_revision": rnd.manifest["ledger_revision"], "created_at": now(),
           "summary": args.reason, "reason": args.reason,
           "sentence_keys": {x: keys[x] for x in ids},
           "sentence_results": {x: "PASS" for x in ids}}
    save_json(folder / f"{chunk['id']}-editor_waiver-{number}.json", rec)
    print(f"waived {','.join(ids)} of {chunk['id']} for {','.join(roles)}")
    return 0


#: Files and folders of a round that ``gc --compact`` removes: raw reports, packets,
#: sentence maps and snapshots are bulk; the logbook (``reviews/*.json``), the
#: manifest, the session and the audit stay.
COMPACT_TARGETS = ("packets", "sentence-maps", "jobs", "candidate-snapshot.txt",
                   "reviews/raw", "reviews/incoming")


def dir_size(path: Path) -> int:
    r"""Total size in bytes of the files below a path.

    Parameters
    ----------
    path : Path
        File or folder.

    Returns
    -------
    int
        Size in bytes.
    """
    if path.is_file():
        return path.stat().st_size
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def cmd_gc(args: argparse.Namespace) -> int:
    r"""List the rounds past their retention; optionally compact the expired ones.

    A round expires a number of days after its last record: ``--closed-days``
    for the status ``superseded`` or ``closed``, ``--ready-days`` for ``ready``.
    A round that is ``active`` or ``needs_user`` never expires, but is reported
    as stale after ``--stale-days`` without a record.  Nothing is deleted
    unless ``--compact`` is given, and then only the bulk of expired rounds
    (see ``COMPACT_TARGETS``); the logbook, manifest, session and audit stay.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``gc`` sub-command.

    Returns
    -------
    int
        Exit code.
    """
    root = root_of(args)
    base = root / ".physics-edit"
    today = dt.datetime.now(dt.timezone.utc)
    rows = []
    for session in sorted(base.glob("*/runs/*/session.md")) if base.exists() else []:
        folder = session.parent
        keys = read_keys(session)
        stamps = [r.get("created_at", "") for r in (
            load_json(p) for p in (folder / "reviews").glob("*.json"))] if (folder / "reviews").exists() else []
        stamps.append(keys.get("created_at", ""))
        last = max((x for x in stamps if x), default="")
        try:
            when = dt.datetime.strptime(last[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
        except ValueError:
            when = dt.datetime.fromtimestamp(session.stat().st_mtime, dt.timezone.utc)
        age = (today - when).total_seconds() / 86400
        status = keys.get("round_status", "?")
        limit = {"superseded": args.closed_days, "closed": args.closed_days,
                 "ready": args.ready_days}.get(status)
        compacted = (folder / "COMPACTED").exists()
        if compacted:
            state = "compacted"
        elif limit is not None and age >= limit:
            state = "EXPIRED"
        elif limit is None and age >= args.stale_days:
            state = "STALE"
        else:
            state = "keep"
        bulk = sum(dir_size(folder / t) for t in COMPACT_TARGETS if (folder / t).exists())
        rows.append((folder, status, last[:10] or "-", age, dir_size(folder), bulk, state))
    print(f"{'round':58}{'status':12}{'last record':>12}{'days':>6}{'MB':>7}{'bulk MB':>9}  state")
    for folder, status, last, age, size, bulk, state in rows:
        name = str(folder.relative_to(base))
        print(f"{name[-57:]:58}{status:12}{last:>12}{age:6.0f}{size / 1e6:7.1f}{bulk / 1e6:9.1f}  {state}")
    expired = [r for r in rows if r[6] == "EXPIRED"]
    if not args.compact:
        print(f"{len(expired)} expired; `gc --compact` removes their bulk "
              f"({sum(r[5] for r in expired) / 1e6:.1f} MB) and keeps the logbook")
        return 0
    freed = 0
    for folder, *_ , bulk, state in rows:
        if state != "EXPIRED":
            continue
        removed = []
        for target in COMPACT_TARGETS:
            path = folder / target
            if path.is_dir():
                shutil.rmtree(path)
                removed.append(target)
            elif path.exists():
                path.unlink()
                removed.append(target)
        (folder / "COMPACTED").write_text(f"compacted {now()}; removed: {', '.join(removed)}\n")
        freed += bulk
    print(f"compacted {len(expired)} rounds, freed {freed / 1e6:.1f} MB")
    return 0


def cmd_defect(args: argparse.Namespace) -> int:
    r"""Log or rule a defect of the author's source.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``defect`` sub-command.

    Returns
    -------
    int
        Exit code.
    """
    rnd = find_round(root_of(args), args.round)
    defects = rnd.manifest.setdefault("source_defects", [])
    if args.action == "add":
        if any(d["id"] == args.id for d in defects):
            return fail(f"defect {args.id} exists")
        defects.append({"id": args.id, "chunk": args.chunk or "", "text": args.text or "",
                        "status": "open", "owner_ruling": "", "created_at": now()})
    else:
        hit = [d for d in defects if d["id"] == args.id]
        if not hit:
            return fail(f"no defect {args.id}")
        hit[0].update({"status": "ruled", "owner_ruling": args.text or ""})
    save_json(rnd.folder / "manifest.json", rnd.manifest)
    print(f"defect {args.id}: {args.action}")
    return 0


def cmd_revision(args: argparse.Namespace) -> int:
    r"""Bump the context or ledger revision (every review becomes stale).

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``revision`` sub-command.

    Returns
    -------
    int
        Exit code.
    """
    rnd = find_round(root_of(args), args.round)
    man = rnd.manifest
    verdicts = [r for r in rnd.reviews() if r.get("role") in (
        "sentence_reviewer", "terminology_reviewer", "editor_waiver", "editor_closure")
        and r.get("context_revision") == man["context_revision"]
        and r.get("ledger_revision") == man["ledger_revision"]]
    print(f"a bump discards {len(verdicts)} current records (every chunk needs its reviews again) "
          f"and rejects {len(rnd.open_packets())} open packets")
    if not args.yes:
        print("nothing changed; if the change of the spine, the ledger or the conventions "
              "affects what reviewers judge, repeat with --yes")
        return 2
    if args.ledger:
        path = rnd.folder / "object-ledger.md"
        path.write_text(re.sub(r"(?m)^revision:.*$", f"revision: {args.ledger}",
                               path.read_text(), count=1))
        rnd.manifest["ledger_revision"] = args.ledger
    if args.context:
        path = rnd.folder / "section-brief.md"
        path.write_text(re.sub(r"(?m)^context_revision:.*$",
                               f"context_revision: {args.context}", path.read_text(), count=1))
        rnd.manifest["context_revision"] = args.context
    save_json(rnd.folder / "manifest.json", rnd.manifest)
    print("revision updated; earlier reviews are stale")
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    r"""Copy the live source to ``candidate-snapshot.txt``.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``snapshot`` sub-command.

    Returns
    -------
    int
        Exit code.
    """
    rnd = find_round(root_of(args), args.round)
    (rnd.folder / "candidate-snapshot.txt").write_text(rnd.live_text)
    print(f"candidate snapshot = live text ({rnd.whole_hash()[:10]})")
    return 0


def fail(message: str) -> int:
    r"""Print an error and return the malformed-input exit code.

    Parameters
    ----------
    message : str
        What is wrong.

    Returns
    -------
    int
        Always 2.
    """
    print(f"ERROR: {message}", file=sys.stderr)
    return 2


# ---------------------------------------------------------------------------
# the gate
# ---------------------------------------------------------------------------

def claim_checks(rnd: Round, fixes: list[str], decisions: list[str]) -> None:
    r"""The status files may not claim more than the gate allows.

    Parameters
    ----------
    rnd : Round
        A loaded round.
    fixes : list of str
        Blocking problems found so far; extended in place.
    decisions : list of str
        Open decisions found so far.
    """
    allowed = "needs_user" if decisions else ("needs_fix" if fixes else "ready")
    if rnd.session.get("round_status") == "ready" and allowed != "ready":
        fixes.append(f"session.md claims round_status ready but the gate allows {allowed}")
    result = rnd.folder / "result.yaml"
    if (result.exists() and allowed != "ready"
            and re.search(r"(?m)^completion:\s*ready\b", result.read_text())):
        fixes.append(f"result.yaml claims completion ready but the gate allows {allowed}")


def evaluate(rnd: Round) -> tuple[list[str], list[str], list[str]]:
    r"""Check a round against the skill.

    Parameters
    ----------
    rnd : Round
        A loaded round.

    Returns
    -------
    tuple of three lists of str
        ``(fixes, decisions, notes)``: blocking problems that need an edit or
        a review, open decisions of the owner, and non-blocking remarks.
    """
    fixes: list[str] = []
    decisions: list[str] = []
    notes: list[str] = []
    folder, session, manifest = rnd.folder, rnd.session, rnd.manifest

    # -- layout -------------------------------------------------------------
    for name in ("session.md", "source-original.txt", "source-boundaries.json",
                 "candidate-snapshot.txt", "section-brief.md", "object-ledger.md",
                 "manifest.json", "completion-audit.md", "reviews"):
        if not (folder / name).exists():
            fixes.append(f"missing {name}")
    current = folder.parent.parent / "CURRENT"
    if not current.exists() or current.read_text().strip() != f"runs/{folder.name}":
        fixes.append("CURRENT does not point to this round")

    try:
        load_policy(rnd.root)
    except PolicyMissing as err:
        fixes.append(str(err))

    # -- session ------------------------------------------------------------
    if session.get("harness_version") != "2":
        fixes.append("session.md: harness_version must be 2")
    if session.get("round_id") != folder.name or manifest.get("round_id") != folder.name:
        fixes.append("round_id of session.md / manifest.json differs from the folder name")
    for key, allowed in SESSION_ENUMS.items():
        if session.get(key) not in allowed:
            fixes.append(f"session.md: {key} = {session.get(key)!r}, expected one of {sorted(allowed)}")
    if session.get("source_file") != manifest.get("source_file"):
        fixes.append("session.md and manifest.json name different source files")
    for key in ATTESTATIONS:
        ok = ("yes", "n/a") if key == "stage_b_parallel_template_done" else ("yes",)
        if session.get(key) not in ok:
            fixes.append(f"attestation {key} is {session.get(key)!r}, must be {' or '.join(ok)}")

    # -- risk consistency (adaptive-routing.md) -------------------------------
    risk, profile = session.get("scientific_risk"), session.get("review_profile")
    scope = session.get("formal_review_scope")
    if session.get("edit_intent") == "substantive" and risk == "low":
        fixes.append("a substantive edit is at least medium risk")
    if risk == "high" and profile != "high_risk":
        fixes.append("high scientific risk requires review_profile high_risk")
    if profile == "high_risk" and scope != "all_in_scope":
        fixes.append("review_profile high_risk requires formal_review_scope all_in_scope")
    if manifest.get("source_defects") and (risk != "high" or profile != "high_risk"):
        fixes.append("a defect of the author's source was logged: risk must be high, profile high_risk")
    if scope == "none":
        has_formal = bool(re.search(r"\$|\\begin\{(equation|align)", rnd.live_text))
        if has_formal or not session.get("formal_none_reason"):
            fixes.append("formal_review_scope none is allowed only without formal content and with formal_none_reason")

    # -- text, snapshots, revisions ------------------------------------------
    original = folder / "source-original.txt"
    if original.exists() and sha(original.read_text()) != manifest.get("source_original_sha256"):
        fixes.append("source-original.txt changed (it must be immutable)")
    snap = folder / "candidate-snapshot.txt"
    whole = rnd.whole_hash()
    if snap.exists() and sha(normalized(snap.read_text().splitlines())) != whole:
        fixes.append("candidate-snapshot.txt differs from the live text; run `snapshot` after the last edit")
    brief, ledger = folder / "section-brief.md", folder / "object-ledger.md"
    for path, key, want in ((brief, "context_revision", manifest.get("context_revision")),
                            (ledger, "revision", manifest.get("ledger_revision"))):
        if path.exists():
            if "TODO" in path.read_text():
                fixes.append(f"{path.name} still contains TODO")
            if read_keys(path).get(key) != want:
                fixes.append(f"{path.name}: {key} differs from manifest.json ({want})")
    audit = folder / "completion-audit.md"
    if audit.exists():
        m = re.search(r"Deviations from the skill:\s*(.*)", audit.read_text())
        if not m or not m.group(1).strip() or m.group(1).strip().startswith("TODO"):
            fixes.append("completion-audit.md has no 'Deviations from the skill:' line")

    # -- chunks ---------------------------------------------------------------
    chunks = manifest.get("chunks", [])
    expect, covered = 1, True
    for chunk in chunks:
        if chunk["first_unit"] != expect:
            covered = False
        expect = chunk["last_unit"] + 1
    if not chunks or not covered or expect != len(rnd.units) + 1:
        fixes.append("the chunks do not partition the units of the live text; the text gained or "
                     "lost a bullet or block since the last chunking (run `rechunk`)")
        claim_checks(rnd, fixes, decisions)
        return fixes, decisions, notes
    records = rnd.reviews()
    for chunk in chunks:
        cid, text_hash = chunk["id"], rnd.chunk_hash(chunk)
        ids = [sid for sid, _ in chunk_sentences(rnd.units, chunk)]
        if len(ids) > MAX_SENTENCES and not (chunk.get("oversized") and
                                            chunk.get("oversized_reason") and
                                            not chunk["oversized_reason"].startswith("TODO")):
            fixes.append(f"{cid}: {len(ids)} sentences (limit {MAX_SENTENCES}) without a named oversized reason")
        mine = [r for r in records if r.get("chunk_id") == cid]
        cur = [r for r in mine if r.get("snapshot_sha256") == text_hash
               and r.get("context_revision") == manifest["context_revision"]
               and r.get("ledger_revision") == manifest["ledger_revision"]]

        def latest(role: str) -> dict | None:
            """Newest current record of a role."""
            hits = [r for r in cur if r["role"] == role]
            return hits[-1] if hits else None

        closure = latest("editor_closure")
        if closure is None:
            fixes.append(f"{cid}: no editor_closure record for the current text")
        keys = chunk_keys(rnd.units, chunk)
        for role, label in (("sentence_reviewer", "sentence review"),
                            ("terminology_reviewer", "terminology-and-notation review")):
            cov = rnd.coverage(role, chunk)
            stale = [sid for sid, key in keys.items() if key not in cov]
            bad = {sid: cov[key][0] for sid, key in keys.items()
                   if key in cov and cov[key][0] != "PASS"}
            if stale:
                fixes.append(f"{cid}: no current {label} verdict for {stale} "
                             "(new or changed since their last review; `pending` lists them)")
            if bad:
                fixes.append(f"{cid}: {label} of the current text is not all PASS ({bad})")
            closes = [r for r in records if r.get("chunk_id") == cid and r.get("role") == role
                      and (r.get("close") or "scope" not in r)
                      and r.get("context_revision") == manifest["context_revision"]
                      and r.get("ledger_revision") == manifest["ledger_revision"]]
            if not closes:
                fixes.append(f"{cid}: no close {label} (a whole-chunk review issued when "
                             "nothing was pending)")
            n_reviews = len([r for r in mine if r.get("role") == role])
            if n_reviews > MAX_REVIEWS_BEFORE_NOTE:
                notes.append(f"{cid}: {n_reviews} {label}s; a sentence flagged a third time goes to "
                             "the owner as a decision instead of another rewrite")
            if closure is not None:
                at_text = [r for r in cur if r["role"] == role]
                if at_text and closure["created_at"] > at_text[-1]["created_at"]:
                    fixes.append(f"{cid}: editor closure was recorded after the {label} "
                                 f"of the current text ({at_text[-1]['_file']})")
        for rec in cur:
            if rec["role"] != "editor_closure" and rec.get("verification_independence") == "unavailable":
                notes.append(f"{cid}: {rec['_file']} verification independence unavailable")
            if "USER_DECISION" in json.dumps(rec.get("sentence_results", {})) + json.dumps(rec.get("quality", {})):
                decisions.append(f"{cid}: USER_DECISION in {rec['_file']}")
        # specialists owed for every earlier hit of this chunk
        for rec in mine:
            if rec["role"] != "sentence_reviewer":
                continue
            for principle, status in rec.get("principle_hits", {}).items():
                if status not in ("FIX", "USER_DECISION"):
                    continue
                served = any(
                    s["role"] == "principle_specialist" and principle in s.get("principles", [])
                    and s["created_at"] >= rec["created_at"] for s in mine)
                if principle in ("P03", "P15"):
                    served = served or any(
                        s["role"] == "terminology_reviewer" and s["created_at"] >= rec["created_at"]
                        for s in mine)
                if not served:
                    fixes.append(f"{cid}: principle {principle} was hit ({rec['_file']}) "
                                 f"but no specialist ran afterwards")

    # -- section-wide review (Stage E) -------------------------------------
    sec = [r for r in records if r.get("chunk_id") == "section"
           and r.get("snapshot_sha256") == whole
           and r.get("context_revision") == manifest["context_revision"]
           and r.get("ledger_revision") == manifest["ledger_revision"]]
    holistic = [r for r in sec if r["role"] == "holistic_reviewer"]
    formal = [r for r in sec if r["role"] == "formal_reviewer"]
    if not holistic:
        fixes.append("section: no holistic review of the current whole text (Stage E)")
    else:
        q = holistic[-1]["quality"]
        for axis in ("scientific_fidelity", "terminology_notation", "prose"):
            if q.get(axis) != "PASS":
                fixes.append(f"section: holistic axis {axis} is {q.get(axis)!r}")
        if q.get("physics_lead") not in ("PASS", "N/A"):
            fixes.append(f"section: holistic axis physics_lead is {q.get('physics_lead')!r}")
    if scope != "none":
        if not formal:
            fixes.append("section: no formal review of the current whole text")
        else:
            rec = formal[-1]
            if rec["quality"].get("formal_validity") != "PASS":
                fixes.append(f"section: formal_validity is {rec['quality'].get('formal_validity')!r}")
            if rec.get("formal_review_scope") != scope:
                fixes.append(f"section: formal review ran with scope {rec.get('formal_review_scope')!r}, "
                             f"session requires {scope!r}")
    if profile == "high_risk":
        for rec in holistic[-1:] + formal[-1:]:
            if not rec.get("blind"):
                fixes.append(f"section: {rec['role']} was not blind (high_risk requires it)")
    for rec in sec:
        if "USER_DECISION" in json.dumps(rec.get("quality", {})):
            decisions.append(f"section: USER_DECISION in {rec['_file']}")

    # -- source defects (unattended rule) -----------------------------------
    for defect in manifest.get("source_defects", []):
        if defect["status"] != "ruled" or not defect.get("owner_ruling"):
            decisions.append(f"open defect {defect['id']}: {defect['text'][:70]}")

    claim_checks(rnd, fixes, decisions)
    return fixes, decisions, notes


def cmd_check(args: argparse.Namespace) -> int:
    r"""Validate a round and print the verdict.

    Parameters
    ----------
    args : argparse.Namespace
        Arguments of the ``check`` sub-command.

    Returns
    -------
    int
        0 if ``ready`` is allowed, 1 if not, 2 if the round cannot be read.
    """
    try:
        rnd = find_round(root_of(args), args.round)
    except (OSError, KeyError, json.JSONDecodeError) as err:
        return fail(f"cannot read the round: {err}")
    fixes, decisions, notes = evaluate(rnd)
    for line in fixes:
        print(f"FIX       {line}")
    for line in decisions:
        print(f"DECISION  {line}")
    for line in notes:
        print(f"note      {line}")
    allowed = "needs_user" if decisions else ("needs_fix" if fixes else "ready")
    print(f"\nround {rnd.folder.name}: gate allows completion = {allowed} "
          f"({len(fixes)} fixes, {len(decisions)} decisions)")
    return 0 if allowed == "ready" else 1


def build_parser() -> argparse.ArgumentParser:
    r"""Command-line parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser with one sub-command per function above.
    """
    top = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    top.add_argument("--root", help="repository root (default: top level of the current git repository)")
    sub = top.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="create a round")
    p.add_argument("slug")
    p.add_argument("source", help="source file relative to the repository root")
    p.add_argument("--round-id")
    p.add_argument("--coverage", default="selective", choices=sorted(SESSION_ENUMS["language_coverage"]))
    p.add_argument("--intent", default="substantive", choices=sorted(SESSION_ENUMS["edit_intent"]))
    p.add_argument("--risk", default="high", choices=sorted(SESSION_ENUMS["scientific_risk"]))
    p.add_argument("--dry-run", action="store_true", help="show the chunk plan only")
    p.set_defaults(func=cmd_init)

    for name, func, helptext in (("chunks", cmd_chunks, "list chunks, write sentence maps"),
                                 ("pending", cmd_pending, "list sentences without a current PASS verdict"),
                                 ("check", cmd_check, "validate; exit 0 only if ready"),
                                 ("snapshot", cmd_snapshot, "copy the live text to candidate-snapshot.txt")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("round", help="round folder or slug")
        p.set_defaults(func=func)

    p = sub.add_parser("policy", help="show or write the role-to-model policy of the project")
    p.add_argument("action", choices=["show", "set"])
    for role in POLICY_ROLES:
        p.add_argument("--" + role.replace("_", "-"), dest=role, metavar="MODEL/EFFORT",
                       help=f"{role}, for example sonnet/high")
    p.set_defaults(func=cmd_policy)

    p = sub.add_parser("waive", help="record that a flagged sentence is right as written")
    p.add_argument("round")
    p.add_argument("--chunk", required=True)
    p.add_argument("--sentences", required=True, help="S05,S07")
    p.add_argument("--roles", help="sentence and/or terminology (default: sentence)")
    p.add_argument("--reason", help="why the sentence is right as written (required)")
    p.set_defaults(func=cmd_waive)

    p = sub.add_parser("gc", help="list rounds past their retention; --compact drops the bulk")
    p.add_argument("--closed-days", type=float, default=7, help="retention of superseded/closed rounds")
    p.add_argument("--ready-days", type=float, default=30, help="retention of ready rounds")
    p.add_argument("--stale-days", type=float, default=14,
                   help="an active round without a record for this long is reported as stale")
    p.add_argument("--compact", action="store_true", help="remove the bulk of expired rounds")
    p.set_defaults(func=cmd_gc)

    p = sub.add_parser("status", help="one dashboard line per chunk")
    p.add_argument("round")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("digest", help="open findings of the recorded reports")
    p.add_argument("round")
    p.add_argument("--chunk")
    p.add_argument("--packet")
    p.set_defaults(func=cmd_digest)

    p = sub.add_parser("prompt", help="build a reviewer packet and print the launch line")
    p.add_argument("round")
    p.add_argument("--chunk", required=True)
    p.add_argument("--role", required=True, help="sentence | terminology | specialist")
    p.add_argument("--scope", choices=["full", "touched", "close"],
                   help="default: full for the first review, touched while sentences are "
                        "pending, close when nothing is pending")
    p.add_argument("--touched", help="S03,S07 (default: every pending sentence)")
    p.add_argument("--principles", help="specialist: P01,P02")
    p.add_argument("--prompts", help="path of review-prompts.md (default: the installed skill)")
    p.set_defaults(func=cmd_prompt)

    p = sub.add_parser("rechunk", help="re-cut the current text into chunks")
    p.add_argument("round")
    p.set_defaults(func=cmd_rechunk)

    p = sub.add_parser("record", help="write one review record")
    p.add_argument("round")
    p.add_argument("--packet", help="packet id issued by `prompt` (hash, scope and keys come from it)")
    p.add_argument("--chunk", help="chunk id or 'section'")
    p.add_argument("--role")
    p.add_argument("--snapshot", help="hash prefix the reviewer was given")
    p.add_argument("--model")
    p.add_argument("--effort")
    p.add_argument("--resolved-model")
    p.add_argument("--principles", help="specialist: P01,P02")
    p.add_argument("--scope", choices=["full", "touched", "close"],
                   help="sentence/terminology review: whole chunk (default), only the touched "
                        "sentences, or the whole chunk at its close")
    p.add_argument("--touched", help="S03,S07 (default: every sentence without a current PASS)")
    p.add_argument("--sentences", help="S03=FIX,S07=USER_DECISION")
    p.add_argument("--default-status", help="verdict of the sentences not listed")
    p.add_argument("--hits", help="P01=FIX,P13=PASS")
    p.add_argument("--axes", help="prose=PASS,terminology_notation=PASS")
    p.add_argument("--formal-scope")
    p.add_argument("--blind", action="store_true")
    p.add_argument("--user-decisions", help="D1,D2 (must be logged with `defect add`)")
    p.add_argument("--summary")
    p.add_argument("--report", help="file with the raw reviewer report")
    p.set_defaults(func=cmd_record)

    p = sub.add_parser("defect", help="log or rule a defect of the author's source")
    p.add_argument("round")
    p.add_argument("action", choices=["add", "rule"])
    p.add_argument("--id", required=True)
    p.add_argument("--chunk")
    p.add_argument("--text", help="description (add) or the owner's ruling (rule)")
    p.set_defaults(func=cmd_defect)

    p = sub.add_parser("revision", help="bump context/ledger revision")
    p.add_argument("round")
    p.add_argument("--ledger")
    p.add_argument("--context")
    p.add_argument("--yes", action="store_true", help="really bump (see the printed cost)")
    p.set_defaults(func=cmd_revision)
    return top


def main(argv: list[str] | None = None) -> int:
    r"""Entry point.

    Parameters
    ----------
    argv : list of str, optional
        Arguments; ``sys.argv[1:]`` if None.

    Returns
    -------
    int
        Exit code of the sub-command.
    """
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except PolicyMissing as err:
        return fail(str(err))


if __name__ == "__main__":
    sys.exit(main())
