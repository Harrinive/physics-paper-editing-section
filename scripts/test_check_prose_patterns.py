r"""Tests of ``check_prose_patterns.py``: each detector finds its pattern and passes clean prose.

Run with ``python3 -m pytest`` from this folder.
"""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import check_prose_patterns as cpp


def run(text, fmt="latex", registry=None, **kw):
    """Analyze a text; ``registry`` is a list of names."""
    reg = [tuple(cpp.words(n)) for n in (registry or [])]
    return cpp.analyze(text, fmt, reg, **kw)


class TestRepeatedPhrases(unittest.TestCase):
    """Given information restated in full."""

    def test_phrase_three_times_in_one_paragraph(self):
        """A noun phrase in full three times within one paragraph is reported."""
        text = ("The effective coupling strength sets the gap. We tune the effective coupling "
                "strength with flux. A larger effective coupling strength closes the gap.\n")
        found = run(text)["repeated_phrases"]
        self.assertEqual([(f["phrase"], f["count"]) for f in found],
                         [("effective coupling strength", 3)])

    def test_two_occurrences_and_short_form_pass(self):
        """Two full uses, followed by the short form, are not reported."""
        text = ("The effective coupling strength sets the gap. We tune the effective coupling "
                "strength with flux. A larger $g$ closes the gap.\n")
        self.assertEqual(run(text)["repeated_phrases"], [])

    def test_restated_in_the_paragraph_after_its_definition(self):
        """A defined name used in full again in the next paragraph is reported."""
        text = ("We call this rate the \\emph{thermal escape rate}. It grows with temperature.\n\n"
                "The thermal escape rate then limits the lifetime of the state.\n")
        found = run(text)["repeated_phrases"]
        self.assertEqual([(f["type"], f["phrase"]) for f in found],
                         [("after_definition", "thermal escape rate")])
        self.assertEqual(found[0]["start"], 3)

    def test_registry_names_replace_ngrams(self):
        """With a registry, only its names are counted, case-insensitively."""
        text = ("The Dressed Qubit Frequency shifts. The dressed qubit frequency drifts. "
                "The dressed qubit frequency returns. Other words other words other words.\n")
        found = run(text, registry=["dressed qubit frequency"])["repeated_phrases"]
        self.assertEqual([f["phrase"] for f in found], ["dressed qubit frequency"])

    def test_comments_are_not_read(self):
        """A phrase that repeats only inside comments is not reported."""
        text = ("The effective coupling strength sets the gap. % effective coupling strength\n"
                "% effective coupling strength again\nIt closes the gap.\n")
        self.assertEqual(run(text)["repeated_phrases"], [])

    def test_phrase_does_not_span_math(self):
        """Words on both sides of an equation do not form one phrase."""
        text = ("The decay rate $\\Gamma$ value grows. The decay rate $\\Gamma$ value falls. "
                "The decay rate $\\Gamma$ value stays.\n")
        phrases = [f["phrase"] for f in run(text)["repeated_phrases"]]
        self.assertNotIn("decay rate value", phrases)


class TestTemplateRuns(unittest.TestCase):
    """Runs of sentences or paragraphs with one opening."""

    def test_three_sentences_with_one_opening(self):
        """Three consecutive sentences that open alike are a run."""
        text = ("The bound on the shift is small. The bound on the width is linear. "
                "The bound on the rate is quadratic. A frame would help.\n")
        found = run(text)["template_runs"]
        self.assertEqual([(f["type"], f["length"], f["opening"]) for f in found],
                         [("sentences", 3, "the bound on")])

    def test_two_sentences_are_not_a_run(self):
        """Two alike openings are not reported."""
        text = "The bound on the shift is small. The bound on the width is linear. It ends.\n"
        self.assertEqual(run(text)["template_runs"], [])

    def test_paragraph_run_by_content_words(self):
        """Paragraphs whose first content words agree form a run."""
        text = ("\\begin{itemize}\n\\item The bound on $\\delta$ is first order.\n"
                "\\item A bound on $\\epsilon$ is first order too.\n"
                "\\item Our bound on $\\gamma$ is first order as well.\n\\end{itemize}\n")
        found = run(text)["template_runs"]
        self.assertEqual([(f["type"], f["length"], f["key"]) for f in found],
                         [("paragraphs", 3, "content words")])


class TestCaptionOverlap(unittest.TestCase):
    """Caption sentences repeated in the citing text."""

    SOURCE = (
        "\\begin{figure}\n\\includegraphics{a.pdf}\n"
        "\\caption{Decay. CAPTION}\n\\label{fig:decay}\n\\end{figure}\n\n"
        "Figure~\\ref{fig:decay} shows TEXT\n")

    def test_verbatim_sentence_is_reported(self):
        """A shared run of at least eight words is reported with its words."""
        same = "the lifetime drops by half when the barrier width grows by $2\\,$nm."
        found = run(self.SOURCE.replace("CAPTION", "Here " + same).replace("TEXT", same))
        hits = found["caption_overlap"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["label"], "fig:decay")
        self.assertGreaterEqual(hits[0]["length"], 8)
        self.assertIn("barrier width", hits[0]["shared"])

    def test_takeaway_in_other_words_passes(self):
        """A caption takeaway that summarizes the text in its own words is not reported."""
        found = run(self.SOURCE.replace("CAPTION", "A wider barrier lengthens the lifetime.")
                    .replace("TEXT", "that the lifetime drops by half when the barrier width "
                                     "grows by two nanometres."))
        self.assertEqual(found["caption_overlap"], [])

    def test_uncited_caption_is_not_compared(self):
        """Text that does not reference the figure is not compared with its caption."""
        same = "the lifetime drops by half when the barrier width grows by two nanometres"
        text = self.SOURCE.replace("CAPTION", same).replace("Figure~\\ref{fig:decay} shows TEXT",
                                                            "We find " + same + ".")
        self.assertEqual(run(text)["caption_overlap"], [])


class TestOutput(unittest.TestCase):
    """Markdown input, line restriction, and the command line."""

    def test_markdown_comments_and_headings(self):
        """Markdown comments are dropped and headings separate paragraphs."""
        text = ("# Title\n\n<!-- the effective coupling strength\nthe effective coupling strength "
                "-->\nThe effective coupling strength sets the gap.\n")
        self.assertEqual(run(text, fmt="markdown")["repeated_phrases"], [])

    def test_restrict_keeps_findings_in_range(self):
        """Only findings that touch the requested lines remain, without the summary."""
        para = ("The effective coupling strength a. The effective coupling strength b. "
                "The effective coupling strength c.\n")
        result = run(para + "\n" + para)
        self.assertEqual(len(result["repeated_phrases"]), 2)
        part = cpp.restrict(result, 3, 3)
        self.assertEqual([f["start"] for f in part["repeated_phrases"]], [3])
        self.assertNotIn("summary", part)

    def test_cli_text_and_json(self):
        """The command line prints a report, or JSON, and exits 0."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.tex"
            path.write_text("The bound on a is small. The bound on b is small. "
                            "The bound on c is small.\n")
            reg = Path(tmp) / "project-vocabulary.json"
            reg.write_text(json.dumps({"terms": [{"term": "bound on a",
                                                  "allowed_names": ["bound"]}]}))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(cpp.main([str(path), "--registry", str(reg)]), 0)
            self.assertIn("3 consecutive sentences", out.getvalue())
            self.assertIn("advisory", out.getvalue())
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(cpp.main([str(path), "--json"]), 0)
            self.assertIn("template_runs", json.loads(out.getvalue()))

    def test_registry_skips_short_names_by_default(self):
        """Two-word registry names are already short forms and are skipped by default."""
        with tempfile.TemporaryDirectory() as tmp:
            reg = Path(tmp) / "r.json"
            reg.write_text(json.dumps({"terms": [{"term": "decay rate",
                                                  "allowed_names": ["thermal escape rate"]}]}))
            self.assertEqual(cpp.registry_phrases(reg), [("thermal", "escape", "rate")])
            self.assertEqual(len(cpp.registry_phrases(reg, min_words=2)), 2)


if __name__ == "__main__":
    unittest.main()
