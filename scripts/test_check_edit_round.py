r"""Tests of ``check_edit_round.py``: a compliant round passes, each violation fails.

Run with ``python3 -m unittest discover -s tools`` from the repository root.
"""

import contextlib
import io
import re
import tempfile
import unittest
from pathlib import Path

import check_edit_round as cer

SOURCE = r"""\section{Demo}
\label{sec:demo}
\subsection{First}
\begin{keypoints}
    \item The first claim is a sentence about the logical qubit.
    % Source: Appendix A.
    \item The second claim has a displayed equation:
    \begin{equation}
        a=b.
    \end{equation}
    where $a$ is the left side.
\end{keypoints}
\subsection{Second}
\begin{keypoints}
    \item The third claim sits in another subsection. It has two sentences.
\end{keypoints}
"""


def write_policy(root):
    """Write a complete policy file, as `policy set` does after the owner answered."""
    roles = {"sentence_reviewer": "sonnet/high", "terminology_reviewer": "sonnet/medium",
             "principle_specialist": "sonnet/high", "faithfulness_specialist": "opus/high",
             "holistic_reviewer": "opus/high", "formal_reviewer": "opus/high",
             "local_polisher": "haiku/high"}
    argv = ["--root", str(root), "policy", "set"]
    for role, value in roles.items():
        argv += ["--" + role.replace("_", "-"), value]
    with contextlib.redirect_stdout(io.StringIO()):
        assert cer.main(argv) == 0


class RoundCase(unittest.TestCase):
    """A temporary repository with one source file and one round."""

    def setUp(self):
        """Create the repository, initialise a round, and fill the templates."""
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "Manuscript").mkdir()
        self.src = self.root / "Manuscript" / "demo.tex"
        self.src.write_text(SOURCE)
        write_policy(self.root)
        self.run_cli("init", "demo", "Manuscript/demo.tex")
        self.folder = next((self.root / ".physics-edit" / "demo" / "runs").iterdir())
        self.manifest = cer.load_json(self.folder / "manifest.json")

    def tearDown(self):
        """Remove the temporary repository."""
        self.tmp.cleanup()

    def run_cli(self, *argv):
        """Run the command line; return (exit code, printed text)."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = cer.main(["--root", str(self.root), *argv])
        return code, out.getvalue()

    def prefix(self, chunk):
        """Current hash prefix of a chunk ('section' for the whole text)."""
        rnd = cer.find_round(self.root, str(self.folder))
        if chunk == "section":
            return rnd.whole_hash()[:12]
        return rnd.chunk_hash(rnd.chunk(chunk))[:12]

    def fill_documents(self):
        """Replace the TODO templates and flip the attestations."""
        for name in ("section-brief.md", "object-ledger.md"):
            path = self.folder / name
            path.write_text(path.read_text().replace("TODO", "done"))
        audit = self.folder / "completion-audit.md"
        audit.write_text("Deviations from the skill: none\n")
        session = self.folder / "session.md"
        text = session.read_text()
        for key in cer.ATTESTATIONS:
            text = re.sub(rf"(?m)^{key}: no$", f"{key}: yes", text)
        session.write_text(text)

    def review_chunk(self, chunk, status="PASS", hits=""):
        """Record closure, sentence review, and terminology review of a chunk."""
        snap = self.prefix(chunk)
        self.run_cli("record", str(self.folder), "--chunk", chunk, "--role", "editor_closure",
                     "--snapshot", snap, "--summary", "closed")
        return (
            self.run_cli("record", str(self.folder), "--chunk", chunk, "--role", "sentence_reviewer",
                         "--snapshot", snap, "--model", "sonnet", "--effort", "high", "--scope", "close",
                         "--default-status", status, "--hits", hits, "--summary", "s"),
            self.run_cli("record", str(self.folder), "--chunk", chunk, "--role", "terminology_reviewer",
                         "--snapshot", snap, "--model", "sonnet", "--effort", "medium", "--scope", "close",
                         "--axes", "terminology_notation=PASS", "--summary", "t"))

    def review_section(self, blind=True):
        """Record the holistic and formal reviews of the whole text."""
        snap = self.prefix("section")
        extra = ["--blind"] if blind else []
        self.run_cli("record", str(self.folder), "--chunk", "section", "--role", "holistic_reviewer",
                     "--snapshot", snap, "--model", "opus", "--effort", "high", *extra,
                     "--axes", "scientific_fidelity=PASS,physics_lead=PASS,terminology_notation=PASS,prose=PASS",
                     "--summary", "h")
        self.run_cli("record", str(self.folder), "--chunk", "section", "--role", "formal_reviewer",
                     "--snapshot", snap, "--model", "opus", "--effort", "high", *extra,
                     "--formal-scope", "all_in_scope", "--axes", "formal_validity=PASS", "--summary", "f")

    def make_ready(self):
        """Bring the round to a state that the gate accepts."""
        self.fill_documents()
        for chunk in self.manifest["chunks"]:
            self.review_chunk(chunk["id"])
        self.review_section()
        self.run_cli("snapshot", str(self.folder))

    def check(self):
        """Run ``check``; return (exit code, output)."""
        return self.run_cli("check", str(self.folder))


class TestGate(RoundCase):
    """Behaviour of the gate."""

    def test_chunks_follow_subsections(self):
        """A new chunk starts at each subsection."""
        self.assertEqual(len(self.manifest["chunks"]), 2)

    def test_fresh_round_is_not_ready(self):
        """Nothing is reviewed yet, so the gate refuses."""
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("editor_closure", out)

    def test_compliant_round_is_ready(self):
        """All records current and attested: exit code 0."""
        self.make_ready()
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_edit_makes_reviews_stale(self):
        """Changing a sentence invalidates the chunk and the section reviews."""
        self.make_ready()
        self.src.write_text(SOURCE.replace("first claim", "initial claim"))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("c01", out)
        self.assertIn("holistic", out)

    def test_comment_edit_keeps_reviews(self):
        """A changed source pointer is not a change of the reviewed text."""
        self.make_ready()
        self.src.write_text(SOURCE.replace("Appendix A", "Appendix B"))
        self.run_cli("snapshot", str(self.folder))
        self.assertEqual(self.check()[0], 0)

    def test_added_bullet_requires_new_chunks(self):
        """The unit list is part of the contract."""
        self.make_ready()
        self.src.write_text(SOURCE.replace(
            "\\end{keypoints}\n\\subsection{Second}",
            "\\item A new claim appears.\n\\end{keypoints}\n\\subsection{Second}"))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("partition", out)

    def test_rechunk_after_splitting_a_bullet(self):
        """Drafting changes the unit count; `rechunk` restores the partition."""
        self.src.write_text(SOURCE.replace(
            "\\item The third claim sits in another subsection. It has two sentences.",
            "\\item The third claim sits in another subsection.\n    \\item It has a second bullet."))
        self.assertIn("partition", self.check()[1])
        self.assertEqual(self.run_cli("rechunk", str(self.folder))[0], 0)
        self.assertNotIn("partition", self.check()[1])
        ids = [c["id"] for c in cer.load_json(self.folder / "manifest.json")["chunks"]]
        self.assertEqual(ids, ["c03", "c04"])

    def test_stale_snapshot_is_rejected_by_record(self):
        """A record cannot attach to text that changed after the review was launched."""
        snap = self.prefix("c01")
        self.src.write_text(SOURCE.replace("first claim", "initial claim"))
        code, out = self.run_cli("record", str(self.folder), "--chunk", "c01", "--role", "editor_closure",
                                 "--snapshot", snap)
        self.assertEqual(code, 2)

    def test_wrong_model_is_rejected(self):
        """The role-to-model table is enforced."""
        snap = self.prefix("c01")
        code, _ = self.run_cli("record", str(self.folder), "--chunk", "c01", "--role", "sentence_reviewer",
                               "--snapshot", snap, "--model", "haiku", "--effort", "high",
                               "--default-status", "PASS")
        self.assertEqual(code, 2)

    def test_fix_verdict_blocks(self):
        """A sentence reviewed as FIX at the current text blocks completion."""
        self.make_ready()
        chunk = self.manifest["chunks"][0]["id"]
        self.review_chunk(chunk, status="FIX", hits="P01=FIX")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("not all PASS", out)

    def test_hit_without_specialist_blocks(self):
        """A principle hit needs a specialist, even after a clean re-review."""
        self.make_ready()
        chunk = self.manifest["chunks"][0]["id"]
        self.review_chunk(chunk, status="PASS", hits="P04=FIX")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("P04", out)
        self.run_cli("record", str(self.folder), "--chunk", chunk, "--role", "principle_specialist",
                     "--principles", "P04,P09,P10", "--snapshot", self.prefix(chunk),
                     "--model", "sonnet", "--effort", "high", "--summary", "x")
        self.assertEqual(self.check()[0], 0)

    def test_faithfulness_specialist_needs_opus(self):
        """P11 is physics faithfulness: Sonnet is refused."""
        chunk = self.manifest["chunks"][0]["id"]
        code, _ = self.run_cli("record", str(self.folder), "--chunk", chunk, "--role", "principle_specialist",
                               "--principles", "P11", "--snapshot", self.prefix(chunk),
                               "--model", "sonnet", "--effort", "high")
        self.assertEqual(code, 2)

    def test_open_defect_needs_user(self):
        """The unattended rule: log, continue, and stay not-ready until ruled."""
        self.make_ready()
        self.run_cli("defect", str(self.folder), "add", "--id", "D1", "--text", "false claim")
        session = self.folder / "session.md"
        session.write_text(session.read_text())  # risk is already high
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("DECISION", out)
        self.run_cli("defect", str(self.folder), "rule", "--id", "D1", "--text", "accepted")
        self.assertEqual(self.check()[0], 0)

    def test_nonblind_review_fails_under_high_risk(self):
        """High risk requires blind holistic and formal reviewers."""
        self.fill_documents()
        for chunk in self.manifest["chunks"]:
            self.review_chunk(chunk["id"])
        self.review_section(blind=False)
        self.run_cli("snapshot", str(self.folder))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("blind", out)

    def test_ready_claim_is_checked(self):
        """round_status ready is refused while the gate says otherwise."""
        session = self.folder / "session.md"
        session.write_text(session.read_text().replace("round_status: active", "round_status: ready"))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("claims round_status ready", out)

    def test_ready_claim_is_checked_even_when_chunks_are_stale(self):
        """The overclaim check does not depend on the chunk partition."""
        session = self.folder / "session.md"
        session.write_text(session.read_text().replace("round_status: active", "round_status: ready"))
        self.src.write_text(SOURCE.replace(
            "\\end{keypoints}\n\\subsection{Second}",
            "\\item A new claim appears.\n\\end{keypoints}\n\\subsection{Second}"))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("claims round_status ready", out)

    def test_section_roles_are_checked_at_record_time(self):
        """A holistic review cannot be filed on a chunk, nor a sentence review on the section."""
        snap = self.prefix("c01")
        code, _ = self.run_cli("record", str(self.folder), "--chunk", "c01", "--role", "holistic_reviewer",
                               "--snapshot", snap, "--model", "opus", "--effort", "high",
                               "--axes", "prose=PASS")
        self.assertEqual(code, 2)

    def test_bad_hit_is_rejected(self):
        """Principle hits must name a principle and a status."""
        snap = self.prefix("c01")
        code, _ = self.run_cli("record", str(self.folder), "--chunk", "c01", "--role", "sentence_reviewer",
                               "--snapshot", snap, "--model", "sonnet", "--effort", "high",
                               "--default-status", "PASS", "--hits", "P99=FIX")
        self.assertEqual(code, 2)

    def test_low_risk_substantive_is_refused(self):
        """A substantive edit cannot be declared low risk."""
        session = self.folder / "session.md"
        session.write_text(session.read_text().replace("scientific_risk: high", "scientific_risk: low"))
        code, out = self.check()
        self.assertIn("at least medium risk", out)


class TestScopedReview(RoundCase):
    """An edit is verified where it happened; the rest keeps its verdicts."""

    def scoped(self, chunk, touched=None):
        """Record closure and scoped sentence and terminology reviews of a chunk."""
        snap = self.prefix(chunk)
        extra = ["--touched", touched] if touched else []
        self.run_cli("record", str(self.folder), "--chunk", chunk, "--role", "editor_closure",
                     "--snapshot", snap, "--summary", "closed")
        self.run_cli("record", str(self.folder), "--chunk", chunk, "--role", "sentence_reviewer",
                     "--snapshot", snap, "--model", "sonnet", "--effort", "high", "--scope", "touched",
                     *extra, "--default-status", "PASS", "--summary", "s")
        return self.run_cli("record", str(self.folder), "--chunk", chunk, "--role", "terminology_reviewer",
                            "--snapshot", snap, "--model", "sonnet", "--effort", "medium", "--scope",
                            "touched", *extra, "--axes", "terminology_notation=PASS", "--summary", "t")

    def test_edit_makes_only_the_edited_sentence_and_its_successor_pending(self):
        """A one-word edit leaves the other sentences and the other chunk alone."""
        self.make_ready()
        self.src.write_text(SOURCE.replace("first claim", "initial claim"))
        code, out = self.run_cli("pending", str(self.folder))
        self.assertIn("c01  sentences  2  sentence review pending: S01,S02", out)
        self.assertIn("c02  sentences  2  sentence review pending: -", out)

    def test_scoped_review_closes_the_edit(self):
        """A scoped review of the pending sentences brings the round back to ready."""
        self.make_ready()
        self.src.write_text(SOURCE.replace("first claim", "initial claim"))
        chunk = self.manifest["chunks"][0]["id"]
        self.assertEqual(self.check()[0], 1)
        code, out = self.scoped(chunk)
        self.assertEqual(code, 0, out)
        self.review_section()
        self.run_cli("snapshot", str(self.folder))
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_fix_on_a_touched_sentence_stays_pending(self):
        """A FIX verdict is not overridden by the unchanged text."""
        self.make_ready()
        self.src.write_text(SOURCE.replace("first claim", "initial claim"))
        chunk = self.manifest["chunks"][0]["id"]
        snap = self.prefix(chunk)
        self.run_cli("record", str(self.folder), "--chunk", chunk, "--role", "sentence_reviewer",
                     "--snapshot", snap, "--model", "sonnet", "--effort", "high", "--scope", "touched",
                     "--sentences", "S01=FIX", "--default-status", "PASS")
        _, out = self.run_cli("pending", str(self.folder))
        self.assertIn("sentence review pending: S01", out)
        self.assertNotIn("sentence review pending: S01,S02", out)

    def test_a_chunk_needs_one_full_review(self):
        """Scoped reviews alone do not close a chunk."""
        self.fill_documents()
        for chunk in self.manifest["chunks"]:
            code, out = self.scoped(chunk["id"])
            self.assertEqual(code, 0, out)
        self.review_section()
        self.run_cli("snapshot", str(self.folder))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("no close sentence review", out)
        self.assertIn("no close terminology-and-notation review", out)

    def test_nothing_to_review_is_refused(self):
        """A scoped review of a fully verified chunk is rejected."""
        self.make_ready()
        chunk = self.manifest["chunks"][0]["id"]
        code, out = self.scoped(chunk)
        self.assertEqual(code, 2, out)

    def test_verdicts_survive_a_rechunk(self):
        """Sentences keep their verdicts under new chunk ids."""
        self.make_ready()
        self.src.write_text(SOURCE + "\\subsection{Third}\n\\begin{keypoints}\n"
                            "    \\item A new claim appears here.\n\\end{keypoints}\n")
        self.run_cli("rechunk", str(self.folder))
        _, out = self.run_cli("pending", str(self.folder))
        pending = [line for line in out.splitlines() if line.startswith("c")]
        self.assertEqual(len(pending), 3)
        self.assertTrue(all("pending: -" in pending[i] for i in (0, 1)), out)
        self.assertNotIn("pending: -", pending[2])


class TestSentences(unittest.TestCase):
    """The sentence splitter."""

    def test_equation_and_abbreviations(self):
        """Equations and 'Sec.~' do not split a sentence."""
        text = ("The map is given in Sec.~\\ref{s}: \\begin{equation}a=b.\\end{equation} "
                "where $x=1$. Another sentence follows.")
        self.assertEqual(len(cer.split_sentences(text)), 2)

    def test_statement_and_proof(self):
        """'Statement ... Proof ...' counts as two sentences."""
        text = "Statement: F is $X_{00}$. Proof: the trace is $d^2$."
        self.assertEqual(len(cer.split_sentences(text)), 2)


if __name__ == "__main__":
    unittest.main()


class TestPackets(RoundCase):
    """prompt, record --packet, status, digest."""

    def setUp(self):
        """Add a minimal review-prompts.md and the registry."""
        super().setUp()
        skills = self.root / "skills" / "physics-paper-editing"
        skills.mkdir(parents=True)
        self.prompts = skills / "review-prompts.md"
        self.prompts.write_text(
            "## Sentence reviewer\n\n```text\nReview the sentences.\n```\n\n"
            "## Terminology-and-notation reviewer\n\n```text\nReview the names.\n```\n\n"
            "## Principle specialist\n\n```text\nSweep PRINCIPLE_IDS.\n```\n")

    def prompt(self, chunk, role, *extra):
        """Run `prompt`; return (code, output)."""
        return self.run_cli("prompt", str(self.folder), "--chunk", chunk, "--role", role,
                            "--prompts", str(self.prompts), *extra)

    def closure(self, chunk):
        """Record the editor closure of the current text of a chunk."""
        return self.run_cli("record", str(self.folder), "--chunk", chunk, "--role", "editor_closure",
                            "--snapshot", self.prefix(chunk), "--summary", "closed")

    def next_id(self):
        """Id of the packet issued last."""
        return f"p{len(list((self.folder / 'packets').glob('p*.json'))):03d}"

    def review(self, chunk, short, statuses=None, **fields):
        """Issue a packet, answer it, record it; return (exit code, output) of `record`."""
        code, out = self.prompt(chunk, short)
        self.assertEqual(code, 0, out)
        pid = self.next_id()
        meta = cer.load_json(self.folder / "packets" / f"{pid}.json")
        results = {sid: "PASS" for sid in meta["covered_ids"]}
        results.update(statuses or {})
        report = self.write_report(pid, sentence_results=results, **fields)
        model, effort = ("sonnet", "high") if short == "sentence" else ("sonnet", "medium")
        return self.run_cli("record", str(self.folder), "--packet", pid, "--report", report,
                            "--model", model, "--effort", effort)

    def write_report(self, meta_id, **fields):
        """Write a JSON report for a packet and return its path."""
        meta = cer.load_json(self.folder / "packets" / f"{meta_id}.json")
        report = {"packet": meta_id, "summary": "r", "findings": []}
        report.update(fields)
        Path(meta["report_file"]).write_text(__import__("json").dumps(report))
        return meta["report_file"]

    def test_packet_contains_scope_and_hash(self):
        """The packet names the sentences and prints the launch line."""
        chunk = self.manifest["chunks"][0]["id"]
        self.closure(chunk)
        code, out = self.prompt(chunk, "sentence")
        self.assertEqual(code, 0, out)
        self.assertIn("launch with model sonnet, effort high", out)
        text = (self.folder / "packets" / "p001.md").read_text()
        self.assertIn("[S01] [scope]", text)
        self.assertIn("Review the sentences.", text)
        self.assertNotIn("source-original", text)

    def test_first_review_then_close_review_makes_the_round_ready(self):
        """First review (full), then the close review once nothing is pending."""
        self.fill_documents()
        for c in self.manifest["chunks"]:
            cid = c["id"]
            self.closure(cid)
            for short in ("sentence", "terminology"):
                code, out = self.review(cid, short)
                self.assertEqual(code, 0, out)
            self.assertIn("scope close", self.prompt(cid, "sentence")[1])
            self.closure(cid)
            for short in ("sentence", "terminology"):
                code, out = self.review(cid, short)
                self.assertEqual(code, 0, out)
        self.review_section()
        self.run_cli("snapshot", str(self.folder))
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_prompt_needs_the_editor_closure(self):
        """No packet for text whose editor closure is not recorded."""
        chunk = self.manifest["chunks"][0]["id"]
        code, out = self.prompt(chunk, "sentence")
        self.assertEqual(code, 2)
        self.assertIn("editor closure", out)

    def test_unrepaired_fix_is_not_reviewed_again(self):
        """A FIX sentence must be repaired or waived before the next touched packet."""
        chunk = self.manifest["chunks"][0]["id"]
        self.closure(chunk)
        self.review(chunk, "sentence", {"S01": "FIX"}, principle_hits={"P01": "FIX"})
        code, out = self.prompt(chunk, "sentence")
        self.assertEqual(code, 2)
        self.assertIn("waive", out)
        code, out = self.run_cli("waive", str(self.folder), "--chunk", chunk, "--sentences", "S01",
                                 "--reason", "the antecedent is the previous bullet")
        self.assertEqual(code, 0, out)
        self.assertIn("scope close", self.prompt(chunk, "sentence")[1])

    def test_waiver_needs_a_reason(self):
        """A waiver without a reason is refused."""
        chunk = self.manifest["chunks"][0]["id"]
        code, _ = self.run_cli("waive", str(self.folder), "--chunk", chunk, "--sentences", "S01")
        self.assertEqual(code, 2)

    def test_close_review_only_when_nothing_is_pending(self):
        """`--scope close` is refused while a sentence is pending."""
        chunk = self.manifest["chunks"][0]["id"]
        self.closure(chunk)
        code, out = self.prompt(chunk, "sentence", "--scope", "close")
        self.assertEqual(code, 2)
        self.assertIn("nothing is pending", out)

    def test_stage_e_waits_for_the_chunks(self):
        """A section review is refused while a chunk has an open item."""
        self.fill_documents()
        snap = self.prefix("section")
        code, out = self.run_cli("record", str(self.folder), "--chunk", "section",
                                 "--role", "holistic_reviewer", "--snapshot", snap, "--model", "opus",
                                 "--effort", "high", "--blind", "--axes", "prose=PASS")
        self.assertEqual(code, 2)
        self.assertIn("settled text", out)

    def test_revision_bump_prints_its_cost_and_needs_yes(self):
        """A bump without --yes changes nothing."""
        code, out = self.run_cli("revision", str(self.folder), "--ledger", "L2")
        self.assertEqual(code, 2)
        self.assertIn("discards", out)
        self.assertEqual(cer.load_json(self.folder / "manifest.json")["ledger_revision"], "L1")
        self.assertEqual(self.run_cli("revision", str(self.folder), "--ledger", "L2", "--yes")[0], 0)

    def test_open_packets_are_listed(self):
        """`status` shows a packet that was issued and not recorded."""
        chunk = self.manifest["chunks"][0]["id"]
        self.closure(chunk)
        self.prompt(chunk, "sentence")
        _, out = self.run_cli("status", str(self.folder))
        self.assertIn("packets out: 1", out)
        self.assertIn("p001", out)

    def test_rechunk_keeps_the_ids_of_reviewed_chunks(self):
        """A late split of one bullet keeps the id of the chunk that was reviewed."""
        c0 = self.manifest["chunks"][0]["id"]
        self.closure(c0)
        self.review(c0, "sentence")
        self.src.write_text(SOURCE.replace("where $a$ is the left side.",
                                           "where $a$ is the left side.\n    \\item A new bullet appears here."))
        self.run_cli("rechunk", str(self.folder))
        ids = [c["id"] for c in cer.load_json(self.folder / "manifest.json")["chunks"]]
        self.assertIn(c0, ids)

    def test_packet_record_survives_an_unrelated_edit(self):
        """An edit elsewhere in the chunk does not discard the verdicts of the other sentences."""
        chunk = self.manifest["chunks"][1]["id"]
        self.closure(chunk)
        self.prompt(chunk, "sentence")
        meta = cer.load_json(self.folder / "packets" / "p001.json")
        report = self.write_report("p001", sentence_results={s: "PASS" for s in meta["covered_ids"]})
        self.src.write_text(SOURCE.replace("third claim", "fourth claim"))
        code, out = self.run_cli("record", str(self.folder), "--packet", "p001", "--report", report,
                                 "--model", "sonnet", "--effort", "high")
        self.assertEqual(code, 0, out)
        self.assertIn("changed since the packet was issued", out)

    def test_wrong_model_and_missing_verdict_are_rejected(self):
        """Policy and coverage are enforced for packets as for hand records."""
        chunk = self.manifest["chunks"][0]["id"]
        self.closure(chunk)
        self.prompt(chunk, "sentence")
        report = self.write_report("p001", sentence_results={"S01": "PASS"})
        code, _ = self.run_cli("record", str(self.folder), "--packet", "p001", "--report", report,
                               "--model", "haiku", "--effort", "high")
        self.assertEqual(code, 2)
        code, out = self.run_cli("record", str(self.folder), "--packet", "p001", "--report", report,
                                 "--model", "sonnet", "--effort", "high")
        self.assertEqual(code, 2, out)
        self.assertIn("no verdict", out)

    def test_digest_lists_open_findings_and_status_runs(self):
        """A FIX finding appears in the digest, and `status` prints a line per chunk."""
        chunk = self.manifest["chunks"][0]["id"]
        self.closure(chunk)
        self.prompt(chunk, "sentence")
        meta = cer.load_json(self.folder / "packets" / "p001.json")
        results = {s: "PASS" for s in meta["covered_ids"]}
        results["S01"] = "FIX"
        report = self.write_report("p001", sentence_results=results, principle_hits={"P01": "FIX"},
                                   findings=[{"sentence": "S01", "principle": "P01",
                                              "severity": "must", "evidence": "ambiguous 'it'",
                                              "repair": "name the claim"}])
        code, out = self.run_cli("record", str(self.folder), "--packet", "p001", "--report", report,
                                 "--model", "sonnet", "--effort", "high")
        self.assertEqual(code, 0, out)
        _, out = self.run_cli("digest", str(self.folder))
        self.assertIn("S01", out)
        self.assertIn("name the claim", out)
        self.assertIn("1 open findings", out)
        _, out = self.run_cli("status", str(self.folder))
        self.assertIn(chunk, out)
        self.assertIn("stage E", out)


class TestPolicy(unittest.TestCase):
    """The project, not the skill, holds the role-to-model policy."""

    def setUp(self):
        """Create a repository without a policy file."""
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "Manuscript").mkdir()
        (self.root / "Manuscript" / "demo.tex").write_text(SOURCE)

    def tearDown(self):
        """Remove the repository."""
        self.tmp.cleanup()

    def run_cli(self, *argv):
        """Run the command line; return (exit code, printed text)."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = cer.main(["--root", str(self.root), *argv])
        return code, out.getvalue()

    def test_init_without_policy_asks_for_it(self):
        """No policy file: `init` refuses and says what to do."""
        code, out = self.run_cli("init", "demo", "Manuscript/demo.tex")
        self.assertEqual(code, 2)
        self.assertIn("ask the owner", out)
        self.assertFalse((self.root / ".physics-edit").exists())

    def test_incomplete_policy_is_refused(self):
        """`policy set` needs every role the first time."""
        code, out = self.run_cli("policy", "set", "--sentence-reviewer", "sonnet/high")
        self.assertEqual(code, 2)
        self.assertIn("still lacks", out)

    def test_policy_roundtrip_and_partial_update(self):
        """A complete policy can be shown, and one role can be changed later."""
        write_policy(self.root)
        code, out = self.run_cli("policy", "show")
        self.assertEqual(code, 0)
        self.assertIn("sentence_reviewer", out)
        code, _ = self.run_cli("policy", "set", "--sentence-reviewer", "opus/xhigh")
        self.assertEqual(code, 0)
        self.assertIn("opus/xhigh", self.run_cli("policy", "show")[1])

    def test_bad_effort_is_refused(self):
        """Only the known effort levels are accepted."""
        write_policy(self.root)
        code, _ = self.run_cli("policy", "set", "--sentence-reviewer", "sonnet/turbo")
        self.assertEqual(code, 2)

    def test_itemize_and_enumerate_are_cut_into_items(self):
        """List environments other than `keypoints` give one unit per item."""
        text = "\\begin{itemize}\n\\item First claim is here.\n\\item Second claim is here.\n\\end{itemize}\n"
        self.assertEqual(len(cer.split_units(text.splitlines())), 2)


class TestRetention(RoundCase):
    """`gc` lists, and compacts only on request."""

    def set_status(self, status):
        """Write a round status into session.md."""
        path = self.folder / "session.md"
        path.write_text(re.sub(r"(?m)^round_status:.*$", f"round_status: {status}", path.read_text()))

    def test_active_round_never_expires(self):
        """An active round is kept (or reported stale), never expired."""
        code, out = self.run_cli("gc", "--stale-days", "999")
        self.assertEqual(code, 0)
        self.assertIn("keep", out)
        self.assertNotIn("EXPIRED", out)

    def test_closed_round_expires_and_listing_deletes_nothing(self):
        """A closed round past its retention is listed, and `gc` alone removes nothing."""
        self.set_status("closed")
        (self.folder / "reviews" / "raw").mkdir()
        (self.folder / "reviews" / "raw" / "x.md").write_text("raw report")
        code, out = self.run_cli("gc", "--closed-days", "0")
        self.assertIn("EXPIRED", out)
        self.assertTrue((self.folder / "reviews" / "raw" / "x.md").exists())

    def test_compact_removes_the_bulk_and_keeps_the_logbook(self):
        """`gc --compact` drops raw reports and sentence maps, keeps manifest and records."""
        self.set_status("closed")
        self.run_cli("chunks", str(self.folder))
        (self.folder / "reviews" / "raw").mkdir()
        (self.folder / "reviews" / "raw" / "x.md").write_text("raw report")
        self.run_cli("record", str(self.folder), "--chunk", self.manifest["chunks"][0]["id"],
                     "--role", "editor_closure", "--snapshot", self.prefix(self.manifest["chunks"][0]["id"]),
                     "--summary", "c")
        code, out = self.run_cli("gc", "--closed-days", "0", "--compact")
        self.assertEqual(code, 0, out)
        self.assertFalse((self.folder / "reviews" / "raw").exists())
        self.assertFalse((self.folder / "sentence-maps").exists())
        self.assertTrue((self.folder / "manifest.json").exists())
        self.assertTrue(list((self.folder / "reviews").glob("*.json")))
        self.assertTrue((self.folder / "COMPACTED").exists())
        self.assertIn("compacted", self.run_cli("gc", "--closed-days", "0")[1])

    def test_ready_round_waits_longer(self):
        """A ready round is expired only after the longer retention."""
        self.set_status("ready")
        self.assertNotIn("EXPIRED", self.run_cli("gc")[1])
        self.assertIn("EXPIRED", self.run_cli("gc", "--ready-days", "0")[1])
