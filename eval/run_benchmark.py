#!/usr/bin/env python3
"""
DevCrew AI benchmark runner.

Place this file and prompts.json in <repo>/eval/ and run from the repo root.

Modes
-----
  e2e        End-to-end runs: POST /projects, then POST /projects/{id}/respond ("approve").
             Measures build success, retries, timing, preview health, plan coverage.
             Needs only the standard library. The backend must be running (uvicorn)
             and Docker must be running.
  accuracy   Calls scope_agent / intent_agent in-process on labeled prompts.
             Run it with the BACKEND virtualenv active (imports backend packages)
             and a valid GROQ_API_KEY in backend/.env.
  all        accuracy, then e2e.
  summarize  Rebuild the summary from a saved results file:  summarize --file <x.jsonl>

Examples
--------
  python eval/run_benchmark.py e2e --limit 3 --delay 40      # smoke test
  python eval/run_benchmark.py e2e --runs 1 --delay 40       # full 30-prompt baseline
  python eval/run_benchmark.py accuracy
  python eval/run_benchmark.py summarize --file eval/results/<run>.jsonl

Optional backend patch (backend/app/api/project.py, approved branch of respond_to_plan)
so the benchmark can see real build results. Without it the script falls back to
"preview_url is non-empty" and cannot report retries or classify failures:

    return {
        "project_id": project_id,
        "status": execution_result["status"],
        "preview_url": execution_result["preview_url"],
        "build_success": execution_result.get("build_success", False),
        "retry_count": execution_result.get("retry_count", 0),
        "build_error": (execution_result.get("build_error") or "")[-500:],
    }

Outcomes recorded per run
-------------------------
  success                   build passed (after 0..3 automatic fixes)
  code_failure              build still failing after the fix loop (real code problem)
  infra_failure             Docker / dependency problem, NOT a code problem
  scope_rejected            Scope Agent rejected an in-scope prompt (false reject)
  approval_not_recognized   "approve" was not understood as approval
  server_error              HTTP 5xx or connection error (e.g. LLM rate limit)
  timeout                   request exceeded --timeout
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import re
import subprocess
import sys
import time
import uuid
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import mean

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
RESULTS_DIR = EVAL_DIR / "results"

TIER_ORDER = ["simple", "medium", "hard"]

SECTION_ALIASES = {
    "hero": ["<h1"],
    "header": ["<header", "<nav"],
    "navbar": ["<nav"],
    "navigation": ["<nav"],
    "footer": ["<footer"],
}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def http_json(method, url, payload=None, timeout=900):
    """Small stdlib HTTP helper. Never raises; returns a dict."""
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url, data=body, method=method, headers={"Content-Type": "application/json"}
    )
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as e:  # must come before OSError
        raw = e.read().decode("utf-8", errors="replace")
        status = e.code
    except OSError as e:  # URLError, timeouts, connection refused
        msg = str(e)
        kind = (
            "timeout"
            if isinstance(e, TimeoutError) or "timed out" in msg.lower()
            else "connection_error"
        )
        return {
            "status": None,
            "error": kind,
            "detail": msg[:300],
            "data": None,
            "elapsed": time.time() - start,
        }
    elapsed = time.time() - start
    try:
        parsed = json.loads(raw)
    except ValueError:
        parsed = None
    return {
        "status": status,
        "error": None,
        "detail": "" if parsed is not None else raw[:300],
        "data": parsed,
        "elapsed": elapsed,
    }


def git_commit():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def percentile(values, q):
    """Nearest-rank percentile, q in [0, 1]."""
    if not values:
        return None
    s = sorted(values)
    idx = max(0, min(len(s) - 1, math.ceil(q * len(s)) - 1))
    return s[idx]


def wilson(k, n, z=1.96):
    """95% Wilson score interval for a proportion."""
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def fmt_prop(k, n):
    if n == 0:
        return "n/a (0 runs)"
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({100 * k / n:.1f}%, 95% CI {100 * lo:.0f}-{100 * hi:.0f}%)"


def fmt_secs(v):
    return "n/a" if v is None else f"{v:.1f}s"


def interleave_by_tier(items):
    """simple1, medium1, hard1, simple2, ... so --limit covers all tiers."""
    buckets = {t: [i for i in items if i["tier"] == t] for t in TIER_ORDER}
    out = []
    for idx in range(max(len(b) for b in buckets.values())):
        for t in TIER_ORDER:
            if idx < len(buckets[t]):
                out.append(buckets[t][idx])
    return out


# --------------------------------------------------------------------------- #
# failure classification
# --------------------------------------------------------------------------- #
INFRA_PATTERNS = [
    (r"Unable to find image|pull access denied", "docker_image_missing"),
    (
        r"error during connect|Cannot connect to the Docker daemon|dockerDesktopLinuxEngine"
        r"|docker: Error response from daemon",
        "docker_not_running",
    ),
    (r"sh: next: not found|next: not found|npm ERR! missing script", "dependencies_missing"),
]

CODE_PATTERNS = [
    (r"You're importing a component that needs|needs `use(State|Effect|Ref|Memo)", "missing_use_client"),
    (r"Type error", "type_error"),
    (r"Module not found|Can't resolve", "bad_import"),
    (
        r"Parsing ecmascript|SyntaxError|Syntax Error|Unexpected token|Unterminated|Expected .* but found",
        "syntax_error",
    ),
]


def classify_failure(build_error: str):
    text = build_error or ""
    for pattern, name in INFRA_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return "infra", name
    for pattern, name in CODE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return "code", name
    return "code", ("unknown_no_error_text" if not text.strip() else "other_code_error")


# --------------------------------------------------------------------------- #
# per-run checks
# --------------------------------------------------------------------------- #
def plan_coverage(projects_dir: Path, project_id: str, sections):
    """Heuristic: share of planned sections whose name appears in app/page.tsx.
    'Hero', 'Navbar', 'Footer' use tag-based aliases because they rarely appear verbatim."""
    page = projects_dir / project_id / "app" / "page.tsx"
    if not page.exists() or not sections:
        return None
    text = page.read_text(encoding="utf-8", errors="ignore").lower()
    hits = 0
    for section in sections:
        name = str(section).lower().strip()
        needles = [name] + SECTION_ALIASES.get(name, [])
        if any(n in text for n in needles):
            hits += 1
    return hits / len(sections)


def check_preview(url):
    if not url:
        return None
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None


def stop_preview(project_id):
    """Stop the preview container so ports and memory are freed between runs."""
    try:
        subprocess.run(
            ["docker", "stop", f"preview-{project_id[:8]}"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception:
        pass


# --------------------------------------------------------------------------- #
# end-to-end mode
# --------------------------------------------------------------------------- #
def run_one(args, item, run_idx, projects_dir):
    rec = {
        "id": item["id"],
        "tier": item["tier"],
        "prompt": item["prompt"],
        "run": run_idx,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "outcome": None,
        "project_id": None,
        "plan_seconds": None,
        "build_seconds": None,
        "build_success": None,
        "retry_count": None,
        "failure_kind": None,
        "failure_subtype": None,
        "preview_http": None,
        "plan_coverage": None,
        "patched_api": None,
        "note": "",
    }
    base = args.base_url.rstrip("/")

    # 1) plan
    r = http_json(
        "POST",
        f"{base}/projects",
        {"prompt": item["prompt"], "session_id": f"eval-{uuid.uuid4()}"},
        args.timeout,
    )
    rec["plan_seconds"] = round(r["elapsed"], 2)
    if r["error"]:
        rec["outcome"] = "timeout" if r["error"] == "timeout" else "server_error"
        rec["note"] = f"/projects {r['error']}: {r['detail']}"
        return rec
    if r["status"] != 200 or not isinstance(r["data"], dict):
        rec["outcome"] = "server_error"
        rec["note"] = f"HTTP {r['status']} on /projects: {r['detail']}"
        return rec
    d = r["data"]
    if d.get("status") == "rejected":
        rec["outcome"] = "scope_rejected"
        rec["note"] = str(d.get("reason", ""))[:200]
        return rec
    project_id = d.get("project_id")
    plan = d.get("plan") or {}
    if not project_id:
        rec["outcome"] = "server_error"
        rec["note"] = "no project_id in /projects response"
        return rec
    rec["project_id"] = project_id

    # 2) approve + build (the backend runs the whole graph inside this request)
    r = http_json(
        "POST",
        f"{base}/projects/{project_id}/respond",
        {"message": "approve"},
        args.timeout,
    )
    rec["build_seconds"] = round(r["elapsed"], 2)
    if r["error"]:
        rec["outcome"] = "timeout" if r["error"] == "timeout" else "server_error"
        rec["note"] = f"/respond {r['error']}: {r['detail']}"
        return rec
    if r["status"] != 200 or not isinstance(r["data"], dict):
        rec["outcome"] = "server_error"
        rec["note"] = f"HTTP {r['status']} on /respond (often an LLM rate limit): {r['detail']}"
        return rec
    d = r["data"]
    if d.get("status") in ("awaiting_approval", "rejected") or "error" in d:
        rec["outcome"] = "approval_not_recognized"
        rec["note"] = f"respond returned status={d.get('status')}"
        return rec

    patched = "build_success" in d
    rec["patched_api"] = patched
    build_success = bool(d["build_success"]) if patched else bool(d.get("preview_url"))
    rec["build_success"] = build_success
    rec["retry_count"] = d.get("retry_count")

    if build_success:
        rec["outcome"] = "success"
        rec["preview_http"] = check_preview(d.get("preview_url"))
    else:
        kind, sub = classify_failure(d.get("build_error", ""))
        rec["failure_kind"], rec["failure_subtype"] = kind, sub
        rec["outcome"] = "infra_failure" if kind == "infra" else "code_failure"
        rec["note"] = (d.get("build_error") or "")[-300:]

    rec["plan_coverage"] = plan_coverage(projects_dir, project_id, plan.get("sections", []))
    if not args.keep_previews:
        stop_preview(project_id)
    return rec


def run_e2e(args, data, jsonl_path):
    items = interleave_by_tier(data["in_scope"])
    if args.ids:
        wanted = {x.strip() for x in args.ids.split(",") if x.strip()}
        items = [i for i in items if i["id"] in wanted]
        missing = wanted - {i["id"] for i in items}
        if missing:
            print(f"Unknown prompt ids ignored: {sorted(missing)}")
    if args.limit:
        items = items[: args.limit]
    projects_dir = Path(args.projects_dir) if args.projects_dir else REPO_ROOT / "projects"
    total = len(items) * args.runs
    records, consecutive_infra, consecutive_errors, n = [], 0, 0, 0

    for run_idx in range(1, args.runs + 1):
        for item in items:
            n += 1
            print(f"[{n}/{total}] {item['id']} ({item['tier']}) run {run_idx}: {item['prompt'][:70]}", flush=True)
            rec = run_one(args, item, run_idx, projects_dir)
            records.append(rec)
            with open(jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
            extra = rec["failure_subtype"] or ""
            print(
                f"    -> {rec['outcome']} retries={rec['retry_count']} "
                f"build={fmt_secs(rec['build_seconds'])} {extra}",
                flush=True,
            )

            consecutive_infra = consecutive_infra + 1 if rec["outcome"] == "infra_failure" else 0
            if consecutive_infra >= args.abort_after_infra:
                print(
                    f"\nStopping: {consecutive_infra} infrastructure failures in a row "
                    f"({rec['failure_subtype']}). Fix Docker/dependencies first; "
                    "continuing would only waste LLM tokens.",
                    flush=True,
                )
                return records

            consecutive_errors = (
                consecutive_errors + 1 if rec["outcome"] in ("server_error", "timeout") else 0
            )
            if consecutive_errors >= args.abort_after_errors:
                print(
                    f"\nStopping: {consecutive_errors} server errors in a row. This is usually an LLM "
                    "rate or daily-token limit (look for 'RateLimitError' in the backend terminal). "
                    "Wait for the quota to reset, then re-run only the failed prompts with --ids.",
                    flush=True,
                )
                return records
            if n < total:
                pause = args.delay
                if rec["outcome"] in ("server_error", "timeout"):
                    pause += args.error_cooldown
                time.sleep(pause)
    return records


# --------------------------------------------------------------------------- #
# accuracy mode (in-process calls to the agents)
# --------------------------------------------------------------------------- #
def run_accuracy(args, data):
    backend_dir = Path(args.backend_dir) if args.backend_dir else REPO_ROOT / "backend"
    sys.path.insert(0, str(backend_dir))
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            from app.agents.scope_agent import scope_agent  # type: ignore
            from app.agents.intent_agent import intent_agent  # type: ignore
    except Exception as e:  # noqa: BLE001
        print(
            "Could not import the backend agents. Activate the backend virtualenv and make sure "
            f"backend/.env has GROQ_API_KEY.\n  Error: {type(e).__name__}: {e}"
        )
        return None

    def call(fn, arg):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                return fn(arg), None
        except Exception as e:  # noqa: BLE001
            return None, f"{type(e).__name__}: {str(e)[:150]}"

    scope_rows, intent_rows = [], []
    scope_items = [(i["id"], i["prompt"], True) for i in data["in_scope"]] + [
        (i["id"], i["prompt"], False) for i in data["out_of_scope"]
    ]
    print(f"Scope accuracy: {len(scope_items)} prompts")
    for pid, prompt, expected in scope_items:
        out, err = call(scope_agent, prompt)
        got = bool(out["allowed"]) if out else None
        scope_rows.append({"id": pid, "prompt": prompt, "expected_allowed": expected, "got_allowed": got, "error": err})
        time.sleep(args.accuracy_delay)

    print(f"Intent accuracy: {len(data['intents'])} messages")
    for i, item in enumerate(data["intents"], 1):
        out, err = call(intent_agent, item["message"])
        got = out.get("action") if out else None
        intent_rows.append({"n": i, "message": item["message"], "expected": item["label"], "got": got, "error": err})
        time.sleep(args.accuracy_delay)

    return {"scope": scope_rows, "intent": intent_rows}


def accuracy_markdown(acc):
    lines = ["## Agent accuracy", ""]
    scope = acc["scope"]
    ok = [r for r in scope if r["error"] is None]
    correct = [r for r in ok if r["expected_allowed"] == r["got_allowed"]]
    fr = [r for r in ok if r["expected_allowed"] and not r["got_allowed"]]
    fa = [r for r in ok if not r["expected_allowed"] and r["got_allowed"]]
    n_in = sum(1 for r in ok if r["expected_allowed"])
    n_out = len(ok) - n_in
    lines += [
        f"- Scope Agent accuracy: {fmt_prop(len(correct), len(ok))}",
        f"- False rejects (valid prompt blocked): {fmt_prop(len(fr), n_in)}",
        f"- False accepts (unsupported prompt allowed): {fmt_prop(len(fa), n_out)}",
    ]
    if len(ok) != len(scope):
        lines.append(f"- {len(scope) - len(ok)} scope call(s) errored and are excluded")
    for r in fr + fa:
        kind = "false reject" if r in fr else "false accept"
        lines.append(f"  - {kind}: \"{r['prompt']}\"")

    intent = acc["intent"]
    iok = [r for r in intent if r["error"] is None]
    icorrect = [r for r in iok if r["expected"] == r["got"]]
    lines += ["", f"- Intent Agent accuracy (approve vs modify): {fmt_prop(len(icorrect), len(iok))}"]
    if len(iok) != len(intent):
        lines.append(f"- {len(intent) - len(iok)} intent call(s) errored and are excluded")
    for r in iok:
        if r["expected"] != r["got"]:
            lines.append(f"  - wrong: \"{r['message']}\" expected={r['expected']} got={r['got']}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# summary
# --------------------------------------------------------------------------- #
def summarize(records, meta, acc=None, notes=None):
    L = []
    L.append("# DevCrew AI benchmark summary")
    L.append("")
    if meta:
        L.append(
            f"- Date: {meta.get('date')}  |  Commit: `{meta.get('commit')}`  |  "
            f"Model: {meta.get('model_note')}  |  Runs per prompt: {meta.get('runs')}"
        )
        L.append("")
    for note in notes or []:
        L.append(f"- {note}")
    if notes:
        L.append("")

    if records:
        total = len(records)
        outcomes = Counter(r["outcome"] for r in records)
        built = [r for r in records if r["outcome"] in ("success", "code_failure")]
        succ = [r for r in built if r["outcome"] == "success"]
        patched = bool(built) and all(r.get("retry_count") is not None for r in built)

        L.append("## End-to-end results")
        L.append("")
        L.append("Outcome counts: " + ", ".join(f"{k}={v}" for k, v in sorted(outcomes.items())))
        L.append("")
        L.append(f"- Final build success (runs that reached a build): {fmt_prop(len(succ), len(built))}")
        L.append(f"- Success across ALL runs (infra/server errors count against it): {fmt_prop(len(succ), total)}")
        if patched:
            first = [r for r in built if r["build_success"] and r["retry_count"] == 0]
            initial_failed = [r for r in built if (not r["build_success"]) or r["retry_count"] >= 1]
            recovered = [r for r in initial_failed if r["build_success"]]
            L.append(f"- First-attempt build success: {fmt_prop(len(first), len(built))}")
            L.append(f"- Fix-loop recovery (failed first, passed later): {fmt_prop(len(recovered), len(initial_failed))}")
            L.append(f"- Average fix attempts per run: {mean(r['retry_count'] for r in built):.2f}")
        else:
            L.append("- First-attempt success / recovery / retries: n/a (apply the backend patch to get these)")

        plan_t = [r["plan_seconds"] for r in records if r["plan_seconds"] is not None and r["outcome"] not in ("server_error", "timeout")]
        build_t = [r["build_seconds"] for r in succ if r["build_seconds"] is not None]
        L.append(f"- Time to plan: p50 {fmt_secs(percentile(plan_t, 0.5))}, p95 {fmt_secs(percentile(plan_t, 0.95))}")
        L.append(f"- Approve to preview (successful runs): p50 {fmt_secs(percentile(build_t, 0.5))}, p95 {fmt_secs(percentile(build_t, 0.95))}")
        prev_ok = [r for r in succ if r["preview_http"] == 200]
        L.append(f"- Preview answered HTTP 200 (successful runs): {fmt_prop(len(prev_ok), len(succ))}")
        cov = [r["plan_coverage"] for r in succ if r["plan_coverage"] is not None]
        if cov:
            L.append(f"- Plan section coverage, heuristic (successful runs): {100 * mean(cov):.0f}% average")

        L.append("")
        L.append("### By prompt tier")
        L.append("")
        L.append("| Tier | Runs | Reached build | Success | First-attempt |")
        L.append("|---|---|---|---|---|")
        for tier in TIER_ORDER:
            t_all = [r for r in records if r["tier"] == tier]
            if not t_all:
                continue
            t_built = [r for r in t_all if r["outcome"] in ("success", "code_failure")]
            t_succ = [r for r in t_built if r["outcome"] == "success"]
            if patched:
                t_first = len([r for r in t_built if r["build_success"] and r["retry_count"] == 0])
                first_txt = f"{t_first}/{len(t_built)}"
            else:
                first_txt = "n/a"
            L.append(f"| {tier} | {len(t_all)} | {len(t_built)} | {len(t_succ)}/{len(t_built)} | {first_txt} |")

        fails = [r for r in records if r["outcome"] in ("code_failure", "infra_failure")]
        if fails:
            L.append("")
            L.append("### Failure breakdown")
            L.append("")
            for (kind, sub), count in Counter((r["failure_kind"], r["failure_subtype"]) for r in fails).most_common():
                L.append(f"- {kind}: {sub} x{count}")
        others = [r for r in records if r["outcome"] in ("server_error", "timeout", "scope_rejected", "approval_not_recognized")]
        if others:
            L.append("")
            L.append("### Non-build problems")
            L.append("")
            for r in others:
                L.append(f"- {r['id']} run {r['run']}: {r['outcome']} - {r['note'][:120]}")

    if acc:
        L.append("")
        L.append(accuracy_markdown(acc))

    L.append("")
    L.append(
        "_Notes: success rates exclude nothing silently - both 'reached a build' and 'all runs' "
        "denominators are shown. Plan coverage is a heuristic. Small samples have wide confidence intervals._"
    )
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def load_jsonl(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def merge_records(paths):
    """Merge several result files. A run lost to a server error / timeout (no build outcome,
    typically an LLM rate limit) is replaced by a later record for the same prompt and run
    number. Real build outcomes are never replaced. Returns (records, notes)."""
    merged, order, replaced = {}, [], 0
    for path in paths:
        for rec in load_jsonl(path):
            key = (rec["id"], rec["run"])
            if key not in merged:
                merged[key] = rec
                order.append(key)
            elif merged[key]["outcome"] in ("server_error", "timeout"):
                merged[key] = rec
                replaced += 1
    notes = []
    if len(paths) > 1:
        notes.append(f"Merged {len(paths)} result files.")
    if replaced:
        notes.append(
            f"{replaced} run(s) lost to server errors/timeouts (no build result) were re-run and replaced; "
            "the original error records remain in the raw files."
        )
    return [merged[k] for k in order], notes


def main():
    ap = argparse.ArgumentParser(description="DevCrew AI benchmark runner")
    ap.add_argument("mode", choices=["e2e", "accuracy", "all", "summarize"])
    ap.add_argument("--base-url", default="http://127.0.0.1:8000")
    ap.add_argument("--runs", type=int, default=1, help="runs per prompt (LLM output varies)")
    ap.add_argument("--limit", type=int, default=0, help="only the first N prompts (tiers interleaved)")
    ap.add_argument("--delay", type=float, default=40.0, help="seconds between runs (Groq free tier: 8000 tokens/min)")
    ap.add_argument("--error-cooldown", type=float, default=60.0, help="extra wait after a server error or timeout")
    ap.add_argument("--timeout", type=float, default=900.0, help="per-request timeout in seconds")
    ap.add_argument("--abort-after-infra", type=int, default=2, help="stop after N consecutive infra failures")
    ap.add_argument("--abort-after-errors", type=int, default=3, help="stop after N consecutive server errors/timeouts (rate limits)")
    ap.add_argument("--ids", default="", help="comma-separated prompt ids to run, e.g. m09,s10,m10,h10")
    ap.add_argument("--keep-previews", action="store_true", help="do not stop preview containers")
    ap.add_argument("--projects-dir", default="", help="folder where the backend writes projects (default: <repo>/projects)")
    ap.add_argument("--backend-dir", default="", help="backend folder for accuracy mode (default: <repo>/backend)")
    ap.add_argument("--accuracy-delay", type=float, default=2.0)
    ap.add_argument("--model-note", default="openai/gpt-oss-20b (Groq)")
    ap.add_argument("--file", nargs="+", default=[], help="results .jsonl file(s) to summarize; several files are merged")
    args = ap.parse_args()

    if args.mode == "summarize":
        if not args.file:
            sys.exit("--file is required for summarize")
        paths = [Path(p) for p in args.file]
        records, notes = merge_records(paths)
        meta_path = paths[0].with_suffix(".meta.json")
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        acc_path = paths[0].with_suffix(".accuracy.json")
        acc = json.loads(acc_path.read_text()) if acc_path.exists() else None
        print(summarize(records, meta, acc, notes))
        return

    data = json.loads((EVAL_DIR / "prompts.json").read_text(encoding="utf-8"))
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    commit = git_commit()
    run_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{commit}"
    base = RESULTS_DIR / run_id
    jsonl_path = base.with_suffix(".jsonl")
    meta = {
        "run_id": run_id,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "commit": commit,
        "base_url": args.base_url,
        "model_note": args.model_note,
        "runs": args.runs,
        "delay_seconds": args.delay,
    }
    base.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2))

    acc = None
    if args.mode in ("accuracy", "all"):
        acc = run_accuracy(args, data)
        if acc:
            base.with_suffix(".accuracy.json").write_text(json.dumps(acc, indent=2))

    records = []
    if args.mode in ("e2e", "all"):
        health = http_json("GET", f"{args.base_url.rstrip('/')}/health", timeout=10)
        if health["status"] != 200:
            sys.exit(f"Backend not reachable at {args.base_url} ({health['error'] or health['status']}). Start uvicorn first.")
        records = run_e2e(args, data, jsonl_path)

    report = summarize(records, meta, acc)
    base.with_suffix(".summary.md").write_text(report, encoding="utf-8")
    print("\n" + report)
    print(f"\nSaved: {base.with_suffix('.summary.md')}")


if __name__ == "__main__":
    main()