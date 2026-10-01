#!/usr/bin/env python3
"""Build review response sources from authored prose and preserved reviewer comments.

No experiment is executed. Re-run after manuscript edits to refresh labelled locations.
"""
from pathlib import Path
import hashlib
import json
import re

from response_content import RESPONSES

NOTES = Path(__file__).resolve().parent
ROOT = NOTES.parents[2]
OUTPUT = NOTES.parent / "revised_v1"
MANUSCRIPT = ROOT / "revision/manuscript/revised_v1"
SCAFFOLD = ROOT / "revision/RESPONSE_TO_REVIEWERS.md"
OUTPUT.mkdir(parents=True, exist_ok=True)

TITLE = "Interpretable PM2.5 Forecasting for Urban Air Quality: A Comparative Study of Adaptive Time-Series Models"
SUBMISSION_ID = "ce621eeb-c97a-487c-92cf-d9f1057300d9"
GROUPS = [
    ("Reviewer 1", [f"R1.{i}" for i in range(1, 11)]),
    ("Reviewer 2 — major comments", [f"R2.M{i}" for i in range(1, 12)]),
    ("Reviewer 2 — minor comments", [f"R2.m{i}" for i in range(1, 7)]),
    ("Editorial requirements", [f"E{i}" for i in range(1, 6)]),
]
expected = [point for _, points in GROUPS for point in points]
assert list(RESPONSES) == expected
scaffold = SCAFFOLD.read_text()
comments = {}
for match in re.finditer(r"^### (R1\.\d+|R2\.[Mm]\d+|E\d+)\n(.*?)(?=^### |\Z)", scaffold, re.M | re.S):
    point, body = match.groups()
    comments[point] = "\n".join(line[2:] for line in body.splitlines() if line.startswith("> "))
assert list(comments) == expected and all(comments.values())

aux = (MANUSCRIPT / "manuscript.aux").read_text()
labels = {m.group(1): (m.group(2), int(m.group(3)))
          for m in re.finditer(r"\\newlabel\{([^}]+)\}\{\{([^}]+)\}\{(\d+)\}", aux)}

def location(value):
    if value not in labels:
        assert not re.match(r"^(?:sec|subsec|tab|fig|eq):", value), value
        return value
    number, page = labels[value]
    kind = {"sec": "Section", "subsec": "Section", "tab": "Table", "fig": "Figure", "eq": "Equation"}[value.split(":")[0]]
    return f"{kind} {number}, p. {page}"

def latex(value):
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
        "α": r"$\alpha$", "β": r"$\beta$", "μ": r"$\mu$",
        "₂": r"\textsubscript{2}", "₀": r"\textsubscript{0}",
        "±": r"$\pm$", "×": r"$\times$", "−": r"$-$",
        "–": "--", "—": "---", "“": "``", "”": "''", "’": "'",
        "‘": "`", "…": r"\ldots{}", "\u00a0": " ",
    }
    value = "".join(replacements.get(char, char) for char in value)
    # Long DOI strings are plain bibliographic identifiers, with safe line breaks.
    value = value.replace(r"/data/2.5/air\_pollution/history", r"\nolinkurl{/data/2.5/air_pollution/history}")
    value = value.replace("/v1/era5", r"\nolinkurl{/v1/era5}")
    return re.sub(r"10\.\d{4,9}/[A-Za-z0-9.]+", lambda m: r"\nolinkurl{" + m.group() + "}", value)

intro = (
    "We thank the editor and both reviewers for their careful reading and constructive comments. "
    "We have revised the manuscript and repeated the affected experiments, while retaining the "
    "original study's three model families, two updating regimes and primary 23-week evaluation. "
    "The revised results replace the submitted numerical results where preprocessing, validation "
    "or completion of the evaluation required correction. The replies below describe each action "
    "and its limitations. Changes in the accompanying manuscript are highlighted in yellow."
)
review_note = (
    "Supervisor review draft — 1 October 2026. The scientific responses are drafted against "
    "revised v1. The DOI-linked public code release, final data-availability wording and "
    "clean-environment reproduction remain pending (R2.m6 and E4). Author approval and final "
    "submission checks also remain pending (E5). This draft has not been submitted."
)
location_note = (
    "Locations refer to the accompanying 26-page revised v1 manuscript, using its printed page "
    "numbers. A section's cited page is its starting page; table, figure and equation pages identify "
    "the item itself. These references must be refreshed if the manuscript is edited. Reviewer "
    "wording is reproduced from the decision letter; numbering and whitespace are normalized."
)
md = ["# Response to the editor and reviewers", "", f"**Manuscript:** {TITLE}", "",
      "**Journal:** Scientific Reports", "", f"**Submission ID:** {SUBMISSION_ID}", "",
      f"**Review status:** {review_note}", "", intro, "", location_note, ""]
tex = [r"\documentclass[11pt,a4paper]{article}",
       r"\usepackage[utf8]{inputenc}",
       r"\input{glyphtounicode}\pdfgentounicode=1",
       r"\usepackage[margin=25mm]{geometry}", r"\usepackage{xcolor}",
       r"\usepackage{amsmath}", r"\usepackage{hyperref}",
       r"\hypersetup{colorlinks=true,urlcolor=blue,linkcolor=black,pdftitle={Response to the editor and reviewers},pdfauthor={Moazzam Umer Gondal and coauthors}}",
       r"\setlength{\parindent}{0pt}", r"\setlength{\parskip}{6pt}",
       r"\setlength{\emergencystretch}{3em}", r"\raggedbottom",
       r"\newcommand{\reviewnote}[1]{\par\noindent\colorbox{yellow!25}{\parbox{\dimexpr\linewidth-2\fboxsep\relax}{\small\textbf{Review note:} #1}}\par}",
       r"\begin{document}", r"\begin{center}\Large\bfseries Response to the editor and reviewers\end{center}",
       r"\textbf{Manuscript:} " + latex(TITLE) + r"\par",
       r"\textbf{Journal:} Scientific Reports\par",
       r"\textbf{Submission ID:} " + latex(SUBMISSION_ID) + r"\par",
       r"\reviewnote{" + latex(review_note) + "}", latex(intro), "", latex(location_note), ""]
records = []
for group, points in GROUPS:
    md += [f"## {group}", ""]
    tex += [r"\clearpage", r"\section*{" + latex(group) + "}"]
    for point in points:
        response = RESPONSES[point]
        heading = ("Requirement " if point.startswith("E") else "Comment ") + re.search(r"\d+$", point).group() + f" ({point})"
        resolved = "; ".join(location(v) for v in response["locations"]) + "."
        md += [f"### {heading}", "", *["> " + line for line in comments[point].splitlines()], "", "**Response:**", "", *sum(([p, ""] for p in response["paragraphs"]), []), "**Manuscript location:** " + resolved, ""]
        tex += [r"\begin{samepage}", r"\subsection*{" + latex(heading) + "}",
                r"\textbf{Reviewer comment:}" if not point.startswith("E") else r"\textbf{Editorial requirement:}",
                r"\begin{quote}\small " + latex(comments[point]).replace("\n", "\n\n") + r"\end{quote}", r"\end{samepage}",
                r"\textbf{Response:}", *sum(([latex(p), ""] for p in response["paragraphs"]), []),
                r"\textbf{Manuscript location:} " + latex(resolved)]
        if response.get("pending"):
            md += ["**Pending for submission:** " + response["pending"], ""]
            tex += [r"\reviewnote{" + latex(response["pending"]) + "}"]
        records.append({"id": point, "comment": comments[point], "locations": resolved,
                        "status": "response_drafted_release_pending" if response.get("pending") else "response_drafted_with_stated_limits",
                        "pending": response.get("pending")})
tex += [r"\end{document}"]
(OUTPUT / "response_to_reviewers.md").write_text("\n".join(md))
(OUTPUT / "response_to_reviewers.tex").write_text("\n".join(tex) + "\n")
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
(NOTES / "RESPONSE_MANIFEST.json").write_text(json.dumps({
    "date": "2026-10-01", "submission_id": SUBMISSION_ID, "reviewer_points": 27,
    "editorial_requirements": 5, "submission_ready": False,
    "manuscript_pdf_sha256": sha(MANUSCRIPT / "manuscript.pdf"),
    "manuscript_tex_sha256": sha(MANUSCRIPT / "manuscript.tex"),
    "manuscript_aux_sha256": sha(MANUSCRIPT / "manuscript.aux"),
    "preserved_scaffold_sha256": sha(SCAFFOLD), "responses": records,
}, indent=2, ensure_ascii=False) + "\n")
print("Generated Markdown and LaTeX responses for 27 reviewer comments and 5 editorial requirements.")
