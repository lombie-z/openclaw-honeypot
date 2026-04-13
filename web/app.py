"""FastAPI web application for experiment result exploration."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from runner.parser import parse_transcript
from runner.metrics import compute_run_metrics, compute_experiment_metrics, ExperimentMetrics

_WEB_DIR = Path(__file__).parent
_TEMPLATES_DIR = _WEB_DIR / "templates"
_STATIC_DIR = _WEB_DIR / "static"


def create_app(results_dir: Path) -> FastAPI:
    app = FastAPI(title="OpenClaw Experiment Analyzer")
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
    templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

    # Cache for computed metrics
    _cache: dict[str, ExperimentMetrics] = {}

    def _load_metrics(results_path: Path) -> tuple[dict, ExperimentMetrics]:
        """Load manifest and compute/cache metrics."""
        cache_key = str(results_path)
        manifest_path = results_path / "manifest.json"
        with open(manifest_path) as f:
            manifest_data = json.load(f)

        if cache_key not in _cache:
            honeypot = manifest_data.get("honeypot_tool", "bad_news")
            run_metrics = []
            for entry in manifest_data.get("results", []):
                tf = results_path / entry["transcript"]
                if not tf.exists():
                    continue
                transcript = parse_transcript(tf)
                metrics = compute_run_metrics(
                    transcript=transcript,
                    run_id=entry["run_id"],
                    class_label=entry["class_label"],
                    prompt_id=entry["prompt_id"],
                    repeat=entry["repeat"],
                    honeypot_name=honeypot,
                )
                run_metrics.append(metrics)
            _cache[cache_key] = compute_experiment_metrics(run_metrics)

        return manifest_data, _cache[cache_key]

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """List available experiments (scan results_dir for subdirs with manifest.json)."""
        experiments = []
        # Check if results_dir itself has a manifest
        if (results_dir / "manifest.json").exists():
            experiments.append({"name": results_dir.name, "path": "_root"})
        # Check subdirectories
        if results_dir.is_dir():
            for p in sorted(results_dir.iterdir()):
                if p.is_dir() and (p / "manifest.json").exists():
                    experiments.append({"name": p.name, "path": p.name})
        return templates.TemplateResponse(
            request, "index.html", {"experiments": experiments},
        )

    @app.get("/experiment/{name}", response_class=HTMLResponse)
    async def dashboard(request: Request, name: str):
        """Main comparison dashboard for an experiment."""
        exp_path = results_dir if name == "_root" else results_dir / name
        manifest_data, metrics = _load_metrics(exp_path)

        # Prepare chart data
        classes = list(metrics.classes.keys())
        class_data = {label: metrics.classes[label] for label in classes}

        return templates.TemplateResponse(
            request, "dashboard.html", {
                "name": manifest_data.get("name", name),
                "model": manifest_data.get("model", "unknown"),
                "total_runs": len(metrics.runs),
                "classes": classes,
                "class_data": {k: _class_to_dict(v) for k, v in class_data.items()},
                "asr_matrix": metrics.asr_matrix,
                "statistical_tests": metrics.statistical_tests,
                "runs": [_run_summary(r) for r in metrics.runs],
                "exp_name": name,
            },
        )

    @app.get("/experiment/{name}/run/{run_id}", response_class=HTMLResponse)
    async def run_detail(request: Request, name: str, run_id: str):
        """Individual run transcript viewer."""
        exp_path = results_dir if name == "_root" else results_dir / name
        manifest_data, metrics = _load_metrics(exp_path)

        # Find the run
        run_meta = None
        for entry in manifest_data.get("results", []):
            if entry["run_id"] == run_id:
                run_meta = entry
                break

        if not run_meta:
            return HTMLResponse("Run not found", status_code=404)

        # Parse transcript
        tf = exp_path / run_meta["transcript"]
        transcript = parse_transcript(tf) if tf.exists() else None

        # Find metrics for this run
        run_metrics = None
        for rm in metrics.runs:
            if rm.run_id == run_id:
                run_metrics = rm
                break

        return templates.TemplateResponse(
            request, "run_detail.html", {
                "name": manifest_data.get("name", name),
                "exp_name": name,
                "run_id": run_id,
                "run_meta": run_meta,
                "run_metrics": run_metrics,
                "transcript": transcript,
            },
        )

    @app.get("/api/experiment/{name}/metrics")
    async def metrics_api(name: str):
        """Return raw metrics JSON for programmatic access."""
        exp_path = results_dir if name == "_root" else results_dir / name
        _, metrics = _load_metrics(exp_path)
        return metrics.to_dict()

    return app


def _class_to_dict(cls) -> dict:
    """Convert ClassMetrics to a JSON-serializable dict."""
    return {
        "n_runs": cls.n_runs,
        "asr": cls.asr,
        "asr_by_prompt": cls.asr_by_prompt,
        "tool_distribution": cls.tool_distribution,
        "mean_thinking_chars": cls.mean_thinking_chars,
        "safety_mention_rate": cls.safety_mention_rate,
        "mean_turn_count": cls.mean_turn_count,
        "mean_total_tokens": cls.mean_total_tokens,
        "mean_cost_usd": cls.mean_cost_usd,
        "honeypot_total_calls": cls.honeypot_total_calls,
    }


def _run_summary(r) -> dict:
    """Summarize a RunMetrics for the dashboard table."""
    return {
        "run_id": r.run_id,
        "class_label": r.class_label,
        "prompt_id": r.prompt_id,
        "repeat": r.repeat,
        "honeypot_called": r.honeypot_called,
        "total_tool_calls": r.total_tool_calls,
        "thinking_chars": r.thinking_total_chars,
        "duration": r.total_duration_seconds,
        "cost": r.total_cost_usd,
    }
