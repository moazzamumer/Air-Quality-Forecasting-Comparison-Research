"""Assemble Phase 1 findings and a qualified budget from recorded evidence."""
from datetime import datetime, timezone
import json
import platform
import os
from pathlib import Path
import psutil
from .protocol import REVISION, configuration
from .audit import ARTIFACTS, REPORTS, manifest


def read(path):
    return json.loads(path.read_text()) if path.exists() else None


def main():
    originals = manifest()
    audit = read(ARTIFACTS / "data_audit.json")
    checks = read(ARTIFACTS / "protocol_tests.json")
    model_checks = read(ARTIFACTS / "model_checks/results.json")
    pilot_root = ARTIFACTS / "pilots"
    pilots = {name: read(pilot_root / f"{name}_pilot.json") for name in ["prophet", "statsmodels", "neuralprophet"]}
    launcher = read(pilot_root / "launcher_results.json") or []
    n = audit["counts"]["eligible_test_windows"]
    estimate = {}
    if pilots["prophet"]:
        fit = pilots["prophet"]["fit_seconds"]
        count = 2+n+1+2+1
        estimate["prophet"] = {"estimated_fits": count, "pilot_fit_seconds": fit,
                               "linear_fit_budget_hours": count*fit/3600}
    if pilots["statsmodels"]:
        p = pilots["statsmodels"]
        count = 4+n+1+2+1
        estimate["statsmodels"] = {"estimated_fits": count, "pilot_fit_seconds": p["fit_seconds"],
                                  "pilot_iterations": p["optimizer_iterations_completed"],
                                  "pilot_converged": p["converged"]}
        divisor = max(1, p["optimizer_iterations_completed"])
        for it in [50, 200]:
            estimate["statsmodels"][f"linear_budget_hours_{it}_iterations"] = count*p["fit_seconds"]*it/divisor/3600
    if pilots["neuralprophet"]:
        p = pilots["neuralprophet"]
        count = 3*n+3+2+1  # core three seeds both regimes + single-seed sensitivities
        per_epoch = p["fit_seconds"]/max(1,p["epochs_completed"])
        estimate["neuralprophet"] = {"core_and_sensitivity_fits": count,"candidate_fits":2,
                                     "pilot_epochs":p["epochs_completed"],"pilot_fit_seconds":p["fit_seconds"]}
        for epochs in [30,50]:
            # Validation candidates have 30+50 epochs; test settings chosen later.
            estimate["neuralprophet"][f"linear_budget_hours_{epochs}_epochs"] = (count*epochs+80)*per_epoch/3600
    cpu = "unknown"
    for line in Path("/proc/cpuinfo").read_text().splitlines():
        if line.startswith("model name"):
            cpu = line.split(":",1)[1].strip();break
    hardware = {"cpu":cpu,"logical_cpus":psutil.cpu_count(),"system_ram_gib":psutil.virtual_memory().total/1024**3,
                "numerical_threads":configuration()["cpu_threads"],"model_device":"cpu",
                "python":platform.python_version(),"sampling_guard_note":"Pilot group RSS sampled every 0.5 seconds; shared memory may be counted more than once"}
    (ARTIFACTS / "hardware.json").write_text(json.dumps(hardware,indent=2))
    pilot_pass = all(p and p["status"]=="passed_feasibility_and_alignment" for p in pilots.values())
    ready = bool(checks and checks["passed"] and model_checks and pilot_pass)
    summary = {"generated_utc":datetime.now(timezone.utc).isoformat(),"phase1_technical_checks_passed":ready,
               "original_files_unchanged":len(originals),"coverage":audit["counts"],"pilot_records":pilots,
               "pilot_launcher_attempts":launcher,"fit_budget_linear_estimates":estimate,
               "budget_caveats":["Small pilots, especially two neural epochs and ten SARIMAX iterations, do not guarantee full-run timing or convergence",
                  "Expanding histories, broader inputs, optimization retries, preprocessing, predictions, diagnostics and imports add time",
                  "No phase2 accuracy/ranking results exist; no configuration has been selected on validation yet"],
               "remaining_limits":["Retrieval dates and archived response metadata unavailable", "Strict data eligibility reduces coverage to 16 discontinuous weeks",
                  "Actual full SARIMAX convergence and final model settings remain Phase 2 validation tasks"]}
    (ARTIFACTS / "phase1_summary.json").write_text(json.dumps(summary,indent=2))
    lines=["# Phase 1 summary","",f"Technical checks: {'passed' if ready else 'incomplete; see individual records'}. Full research experiments have not started.","",
           "## Workspace and preservation","",f"Revision code, configuration, notebook, reports, tests and generated artifacts are isolated below `revision/`. All {len(originals)} fingerprinted originals remain unchanged, including `main.ipynb` and the submitted manuscript.","",
           "## Established findings","",
           "- Raw data: 39,523 rows, 40,267 calendar hours, 744 missing hours in 21 intervals. The raw file has no empty values, which does not establish continuous sampling.",
           "- Old preprocessing is verified whole-dataset upper z-score row removal: 2,693 rows deleted. It is not the winsorization described in the paper.",
           "- The revised calendar split starts testing at 2025-01-13 01:00. There are 23 full weeks plus a 163-hour terminal window.",
           "- Shared strict availability retains 16 weeks / 2,688 original observed target hours. Availability exclusions and exact dates are saved; this reduces generalizability and must be disclosed.",
           "- Corrected training-only correlation, MI and mRMR results are saved. The original mRMR call is invalid evidence for selecting four gases; the revision labels them predefined and plans an ablation.",
           "- Source code supports UTC interpretation and establishes endpoint/coordinate evidence. Exact retrieval dates and archived response metadata remain unavailable; a provider-availability/start-date discrepancy is also documented.","",
           "## Correctness evidence","",
           f"- {checks['tests_run'] if checks else 0} recorded protocol tests: {'passed' if checks and checks['passed'] else 'pending'}. They check calendar/value preservation, target isolation, training-only transformations, coverage, episode boundaries, forecast extraction and correction timing.",
           "- Synthetic installed-library checks verify a complete raw NeuralProphet horizon against the target-indexed diagonal; `yhat1` alone has only one valid future lead in that example.",
           "- NeuralProphet training uses complete episodes with shared global components/normalization; no gap-crossing windows or synthetic target labels. Its 0.9.0 prediction preprocessing requires a narrowly scoped compatibility path when seasons and unknown future targets are present. Training imputation stays disabled.",
           "- SARIMAX low-memory results need terminal-filter-state initialization for the first state refresh. The wrapper matches normal state updating on the synthetic check, including missing revealed targets, and does not re-estimate parameters.","",
           "## Bounded pilot results","","| Model | Fit time | Forecast time | Peak group RSS | Qualification |","|---|---|---|---|---|"]
    for name,p in pilots.items():
        if p is None:lines.append(f"| {name} | Pending | Pending | Pending | No passed pilot record | ");continue
        attempts=[a for a in launcher if a["model"]==name and a["returncode"]==0]
        mem=f"{attempts[-1]['process_group_peak_rss_mib_sampled']:.1f} MiB" if attempts else "Not recorded"
        qualify=("2 feasibility epochs; not validated accuracy" if name=="neuralprophet" else
                 "10 optimization iterations; convergence not established" if name=="statsmodels" else
                 "additive configuration; validation selection pending")
        lines.append(f"| {name} | {p['fit_seconds']:.2f} s | {p['prediction_seconds']:.3f} s | {mem} | {qualify} |")
    lines += ["","Pilots use 35,568 historical calendar hours before the first training-only validation origin (2024-12-16 01:00), and forecast 168 hours without future target inputs. CPU threads are fixed at two. No pilot MAE/ranking is presented as a research result.","",
              "## Compute estimate","","These are rough linear projections from the recorded pilots, not reserved runtime or measured complete experiments. Budget includes full proposed model-fit counts before any reuse of identical initial fits. Predictions, preprocessing, imports and analysis add overhead; allow for expanding histories and convergence retries.",""]
    if "prophet" in estimate:
        e=estimate["prophet"];lines.append(f"- Prophet: {e['estimated_fits']} fits, approximately {e['linear_fit_budget_hours']:.2f} fit-hours at the pilot rate.")
    if "statsmodels" in estimate and "linear_budget_hours_50_iterations" in estimate["statsmodels"]:
        e=estimate["statsmodels"];lines.append(f"- SARIMAX: {e['estimated_fits']} fits, approximately {e['linear_budget_hours_50_iterations']:.2f}–{e['linear_budget_hours_200_iterations']:.2f} fit-hours projecting 50–200 iterations. Different orders can differ substantially; the short pilot is not convergence evidence.")
    if "neuralprophet" in estimate:
        e=estimate["neuralprophet"];lines.append(f"- NeuralProphet: {e['core_and_sensitivity_fits']} core/sensitivity fits plus two validation candidates, approximately {e['linear_budget_hours_30_epochs']:.2f}–{e['linear_budget_hours_50_epochs']:.2f} fit-hours projecting 30–50 epochs. Three seeds remain in the proposed core matrix.")
    lines += ["","The full matrix remains conditional on these estimates and training-only validation. Use sequential resumable runs, a bounded optimizer with explicit convergence reporting, and checkpointed forecasts. A failed/nonconverged final fit must be recorded and addressed; do not silently relax comparability or count it as a successful convergence check.","",
              "## Phase 2 boundary","",
              "The next work is training-only candidate validation, then the main comparison/baselines/ablations/sensitivities using the documented calendar and information sets. No manuscript or final response claim has been marked complete from this audit alone.","",
              "Metadata that cannot be recovered is a documented limitation, not a reason to invent provenance. Phase 4 must explain it and the reduced evaluation coverage explicitly. Review the compute estimates before committing the machine to full experiments.",""]
    (REPORTS / "PHASE1_SUMMARY.md").write_text("\n".join(lines))
    print(json.dumps({"phase1_technical_checks_passed":ready,"fit_budget_linear_estimates":estimate},indent=2))


if __name__=="__main__":
    main()
