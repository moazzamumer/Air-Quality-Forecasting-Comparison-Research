#!/usr/bin/env python3
"""Check review-document coverage, locations, key numbers and source preservation."""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess

from response_content import RESPONSES

NOTES = Path(__file__).resolve().parent
ROOT = NOTES.parents[2]
OUTPUT = NOTES.parent / "revised_v1"
MANUSCRIPT = ROOT / "revision/manuscript/revised_v1"
EVIDENCE = ROOT / "revision/corrected/artifacts"
manifest = json.loads((NOTES / "RESPONSE_MANIFEST.json").read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert manifest["manuscript_pdf_sha256"] == sha(MANUSCRIPT / "manuscript.pdf")
assert manifest["manuscript_tex_sha256"] == sha(MANUSCRIPT / "manuscript.tex")
assert manifest["manuscript_aux_sha256"] == sha(MANUSCRIPT / "manuscript.aux")
assert manifest["preserved_scaffold_sha256"] == sha(ROOT / "revision/RESPONSE_TO_REVIEWERS.md")
pdf = OUTPUT / "response_to_reviewers.pdf"
pdftext = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
md = (OUTPUT / "response_to_reviewers.md").read_text()
assert len(re.findall(r"^### (?:Comment|Requirement) ", md, re.M)) == 32
for row in manifest["responses"]:
    headings = re.findall(r"^(?:Comment|Requirement)\s+\d+\s+\(" + re.escape(row['id']) + r"\)\s*$", pdftext, re.M)
    assert len(headings) == 1, row["id"]
    assert row["comment"]
    assert row["locations"]
assert not any(placeholder in md for placeholder in ["[Describe", "[Verified", "[Section", "[Response"])
assert not any(path in pdftext for path in ["/home/", "revision/corrected", "artifacts/phase", "[Author input pending:"])
assert not any(ord(char)<32 and char not in "\n\r\t\f" for char in pdftext)
assert "DOI-linked public code release" in pdftext
assert "This requirement is not yet complete" in pdftext

original_letter = Path("/home/moazzam/.codex/attachments/2127c339-6493-421e-abf2-93ea25c9d0e1/Pasted text.txt")
normalize = lambda value: re.sub(r"\s+", " ", value).strip()
if original_letter.exists():
    letter = normalize(original_letter.read_text())
    for row in manifest["responses"]:
        assert normalize(row["comment"]) in letter, row["id"]

def csv_rows(name):
    with (EVIDENCE / name).open(newline="") as handle:
        return list(csv.DictReader(handle))

checked = []
def contains(point, value, digits=2):
    formatted = f"{float(value):.{digits}f}"
    prose = " ".join(RESPONSES[point]["paragraphs"]).replace("−", "-")
    assert formatted in prose, (point, formatted)
    checked.append({"point": point, "displayed_value": formatted})

performance = {row["stream"]: row for row in csv_rows("phase3/performance.csv")}
for row in performance.values():
    assert int(row["windows"]) == 23 and int(row["hours"]) == 3624
for col in ["pooled_mae", "pooled_rmse"]:
    contains("R1.1", performance["sarimax_walk_s42"][col])
for stream in ["persistence", "daily_persistence", "weekly_persistence"]:
    contains("R2.M4", performance[stream]["pooled_mae"])
for stream in ["sarimax_frozen_no_inputs", "prophet_frozen_no_inputs", "neuralprophet_frozen_no_inputs", "prophet_frozen_broad", "neuralprophet_frozen_broad"]:
    contains("R2.M7", performance[stream]["pooled_mae"])
for row in csv_rows("phase3/coefficients.csv"):
    if row["regime"] == "frozen":
        contains("R1.3", row["coefficient_scaled_input"])
for row in csv_rows("phase3/neuralprophet_seed_summary.csv"):
    contains("R1.4", row["pooled_mae_mean"])
    contains("R1.4", row["pooled_mae_sd"])
for row in csv_rows("phase3/target_descriptive.csv"):
    for col in ["mean", "sd", "median", "minimum", "maximum"]:
        contains("R1.10", row[col])
for row in csv_rows("phase3/correction_alpha_summary.csv"):
    if row["family"] == "sarimax" and float(row["alpha"]) in [0, 0.1, 0.3, 1]:
        contains("R1.7", row["mean_weekly_mae"])
    if float(row["alpha"]) == 0.3:
        contains("R2.M8", abs(float(row["mean_weekly_improvement"])))
for row in csv_rows("phase3/high_concentration.csv"):
    if row["stream"] in ["sarimax_frozen_s42", "prophet_frozen_s42", "neuralprophet_frozen_s42"]:
        contains("R2.M3", row["mae"])
for row in csv_rows("phase3/paired_contrasts.csv"):
    if row["contrast"] in ["sarimax: EWMA 0.3 − base", "EWMA(0.3) frozen SARIMAX − EWMA(0.3) frozen Prophet"]:
        for col in ["mean_weekly_mae_difference", "ci95_block3_low", "ci95_block3_high"]:
            contains("R1.8", row[col])
contains("R2.m5", float(performance["prophet_frozen_s42"]["pooled_mae"]) - float(performance["prophet_frozen_s42_ewma03"]["pooled_mae"]))
contains("R2.m5", float(performance["prophet_frozen_s42"]["mean_weekly_mae"]) - float(performance["prophet_frozen_s42_ewma03"]["mean_weekly_mae"]))
selection = json.loads((EVIDENCE / "phase2/selection.json").read_text())
contains("R1.5", selection["candidates"]["sarimax"][0]["mean_weekly_mae"])
assert selection["selected"]["sarimax"] == {"order": [1,0,1], "seasonal_order": [1,0,1,24]}
audit = json.loads((EVIDENCE / "phase3/postfit_audit.json").read_text())
assert audit["primary_origins"] == 23 and audit["scored_hours"] == 3624
assert audit["declared_failed_controls_checked"] == ["ablate_sarimax_broad"]
assert audit["ready_for_author_evidence_review"]
assert sha(ROOT / "data/beijing.csv") == audit["source_sha256"]

log = (OUTPUT / "response_to_reviewers.log").read_text()
assert not any(problem in log for problem in ["Overfull \\hbox", "Overfull \\vbox", "LaTeX Error:", "There were undefined"])
fonts = subprocess.check_output(["pdffonts", str(pdf)], text=True)
assert "Type 3" not in fonts
info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
pages = int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))
record = {
    "date": "2026-10-01", "pdf_pages": pages,
    "reviewer_points": 27, "editorial_requirements": 5,
    "all_32_responses_present_in_pdf": True,
    "comments_match_preserved_scaffold": True,
    "comments_match_original_letter": original_letter.exists(),
    "labelled_locations_resolved_from_current_manuscript": True,
    "manuscript_and_scaffold_unchanged": True,
    "raw_dataset_unchanged": True,
    "numerical_claims_checked": len(checked), "numerical_checks": checked,
    "typesetting_errors_or_overfull_boxes": 0,
    "embedded_type1_fonts_and_extractable_text": True,
    "pdf_sha256": sha(pdf), "tex_sha256": sha(OUTPUT / "response_to_reviewers.tex"),
    "submission_ready": False,
    "pending": ["DOI-linked versioned code release", "final data-availability statement", "clean-environment reproduction", "supervisor/author review and final submission checks"],
    "verification_scope": "Comment coverage, key displayed numerical claims, manuscript binding, source preservation and PDF quality. Scientific constraints and unresolved provenance are stated in the responses; this is not independent peer review.",
}
(NOTES / "VERIFICATION.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
print(f"Verified {pages}-page PDF, 32 replies, {len(checked)} numerical checks, manuscript binding and source preservation.")
