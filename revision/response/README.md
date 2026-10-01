# Point-by-point response — revised v1

Prepared on 1 October 2026 for Moazzam and his supervisor. This is a review draft, not a submitted journal response.

Send these two existing PDFs together for review:

- [Point-by-point response PDF](revised_v1/response_to_reviewers.pdf)
- [Yellow-highlighted revised manuscript PDF](../manuscript/revised_v1/manuscript.pdf)

The response contains all 27 reviewer comments and five editorial requirements, their individual replies and manuscript section/item/page locations. Reviewer wording is preserved from the supplied decision letter. Scientific replies use the approved corrected experiments; local evidence paths are not used as academic citations. Missing retrieval metadata, the failed broad-input SARIMAX control and other substantive limitations are acknowledged.

Yellow review notes flag the DOI-linked code release, final data-availability wording, clean-environment reproduction and author/final submission checks. These are not described as completed. Resolve them after supervisor review before preparing the journal version.

`revised_v1/` contains the PDF, editable Markdown and LaTeX source. `revised_v1_notes/` contains authored response prose, generation/build tools, per-point tracking, manuscript binding and verification. The earlier `revision/RESPONSE_TO_REVIEWERS.md` remains an unchanged planning scaffold.

Compile the existing LaTeX source with `bash revision/response/revised_v1_notes/build_pdf.sh`. This preserves manual source edits. `--regenerate` intentionally replaces Markdown/LaTeX from `response_content.py` and refreshes labelled locations from the manuscript's compiled auxiliary file. Run `python3 revision/response/revised_v1_notes/verify_response.py` afterwards. No model fitting or manuscript editing is performed by these commands.

After any manuscript edit, recompile the manuscript, review the manually specified narrative page ranges, regenerate the response locations and verify both PDFs. The verification record binds this response to the current manuscript hash and will reject stale bindings. If response prose is edited manually, keep `response_content.py` synchronized before regeneration.
