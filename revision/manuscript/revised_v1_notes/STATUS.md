# Revised v1 status

Moazzam approved Phase 4A and manuscript writing on 1 October 2026. He supplied four literature PDFs and authorized relevance-based inclusion; all four have been assessed and included.

Following his R2.M7 feedback, the PM10 exclusion rationale is now supported by an EPA definition and a primary leakage-methodology paper. Implementation states the scope rationale and information-availability distinction; Results qualifies the grouped predictor control. No experiments, numerical tables or figures changed. Both review PDFs and their page references are refreshed; see PM10_RATIONALE.md.

A separate highlighted revised v1 manuscript is drafted and compiled in `../revised_v1/`. Its original flat LaTeX layout, class and bibliography style are preserved. Yellow highlights mark changed text, equations, tables, new headings and new bibliography entries; changed figures have yellow frames and captions. All nine figures use corrected approved evidence. The original 15 submission files are unchanged.

The scientific body is available for author review. Following Moazzam’s feedback, exact choices have been moved to Implementation and Methodology explains the general concepts. The original GitHub URL is restored; results and figures are unchanged. Data/code availability contain two visible author-input placeholders pending a DOI-linked release decision and defensible archive statements. The PDF is a review draft, not submission-ready. The separate point-by-point response is now drafted and compiled in `../../response/revised_v1/`, with all 27 reviewer points, five editorial requirements and current manuscript section/item/page locations checked. Both PDFs can be sent to the supervisor for review. After author edits, response locations must be refreshed; clean-environment reproduction, archive publication and final submission checks remain outstanding.

The build script compiles the existing manuscript by default and preserves manual author edits. Its explicit --regenerate option replaces v1 text/tables and figures from saved evidence before compilation. It does not train models. Standard TeX packages missing locally were downloaded into a temporary user tree, preserving the original class. Build logs and checks are retained here.

Use CHANGE_LOG.md for point-by-point draft mapping and AUTHOR_INPUTS.md for the current pause. No reviewer point is marked closed before manuscript and response verification.
