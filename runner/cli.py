"""CLI entry point for the OpenClaw experiment runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click


@click.group()
def cli():
    """OpenClaw Unicode Honeypot Experiment Tool."""
    pass


@cli.command()
@click.argument("manifest", type=click.Path(exists=True, path_type=Path))
@click.option("--output-dir", "-o", type=click.Path(path_type=Path), default=None,
              help="Directory to store results (default: results/<experiment-name>)")
@click.option("--dry-run", is_flag=True, help="Show what would be executed without running")
def run(manifest: Path, output_dir: Path | None, dry_run: bool):
    """Run an experiment from a YAML manifest."""
    from .config import load_manifest
    from .executor import ExperimentExecutor

    spec = load_manifest(manifest)
    if output_dir is None:
        output_dir = Path("results") / spec.name

    click.echo(f"Experiment: {spec.name}")
    click.echo(f"Model: {spec.model}")
    click.echo(f"Prompts: {len(spec.prompts)}")
    click.echo(f"Run classes: {len(spec.runs)}")
    click.echo(f"Repeats: {spec.repeats}")
    total = len(spec.prompts) * len(spec.runs) * spec.repeats
    click.echo(f"Total runs: {total}")
    click.echo(f"Output: {output_dir}")

    if dry_run:
        click.echo("\n[dry-run] Would execute the above. Exiting.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    executor = ExperimentExecutor(spec, output_dir)
    results = executor.execute_all()

    succeeded = sum(1 for r in results if r.success)
    click.echo(f"\nDone: {succeeded}/{len(results)} runs succeeded")


@cli.command()
@click.argument("results_dir", type=click.Path(exists=True, path_type=Path))
@click.option("--format", "fmt", type=click.Choice(["json", "summary"]), default="summary")
def analyze(results_dir: Path, fmt: str):
    """Analyze collected experiment results."""
    from .parser import parse_transcript
    from .metrics import compute_run_metrics, compute_experiment_metrics

    # Load manifest
    manifest_path = results_dir / "manifest.json"
    if not manifest_path.exists():
        click.echo(f"Error: no manifest.json in {results_dir}", err=True)
        sys.exit(1)

    with open(manifest_path) as f:
        manifest_data = json.load(f)

    honeypot_tool = manifest_data.get("honeypot_tool", "bad_news")

    # Parse all transcripts and compute metrics
    run_metrics = []
    for result_entry in manifest_data.get("results", []):
        transcript_file = results_dir / result_entry["transcript"]
        if not transcript_file.exists():
            click.echo(f"  Warning: missing transcript {transcript_file}", err=True)
            continue

        transcript = parse_transcript(transcript_file)
        metrics = compute_run_metrics(
            transcript=transcript,
            run_id=result_entry["run_id"],
            class_label=result_entry["class_label"],
            prompt_id=result_entry["prompt_id"],
            repeat=result_entry["repeat"],
            honeypot_name=honeypot_tool,
        )
        run_metrics.append(metrics)

    experiment = compute_experiment_metrics(run_metrics)

    if fmt == "json":
        # Write metrics.json
        metrics_path = results_dir / "metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(experiment.to_dict(), f, indent=2, default=str)
        click.echo(f"Metrics written to {metrics_path}")
    else:
        # Print summary table
        click.echo(f"\n{'Class':<25} {'Runs':>5} {'ASR':>8} {'Avg Tokens':>12} {'Avg Cost':>10}")
        click.echo("-" * 65)
        for label, cls_metrics in experiment.classes.items():
            click.echo(
                f"{label:<25} {cls_metrics.n_runs:>5} "
                f"{cls_metrics.asr:>7.1%} "
                f"{cls_metrics.mean_total_tokens:>12.0f} "
                f"${cls_metrics.mean_cost_usd:>9.4f}"
            )


@cli.command()
@click.argument("results_dir", type=click.Path(exists=True, path_type=Path))
@click.option("--port", "-p", type=int, default=8080)
@click.option("--host", type=str, default="127.0.0.1")
def serve(results_dir: Path, port: int, host: str):
    """Start the web UI to explore experiment results."""
    import uvicorn
    from .web_app import create_app

    app = create_app(results_dir)
    click.echo(f"Serving results from {results_dir}")
    click.echo(f"Dashboard: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


@cli.command()
@click.argument("results_dir", type=click.Path(exists=True, path_type=Path))
@click.option("--output-dir", "-o", type=click.Path(path_type=Path), default=Path("deploy"))
def export(results_dir: Path, output_dir: Path):
    """Export all experiment dashboards to static HTML in deploy/."""
    import shutil
    from jinja2 import Environment, FileSystemLoader

    from .parser import parse_transcript
    from .metrics import compute_run_metrics, compute_experiment_metrics

    web_dir = Path(__file__).parent.parent / "web"
    env = Environment(loader=FileSystemLoader(str(web_dir / "templates")))

    exp_dir = output_dir / "experiment"
    exp_dir.mkdir(parents=True, exist_ok=True)

    static_src = web_dir / "static"
    static_dst = output_dir / "static"
    if static_dst.exists():
        shutil.rmtree(static_dst)
    shutil.copytree(str(static_src), str(static_dst))
    click.echo(f"Copied static assets to {static_dst}")

    experiments = []
    for p in sorted(results_dir.iterdir()):
        if not p.is_dir() or p.name.startswith("_") or not (p / "manifest.json").exists():
            continue

        with open(p / "manifest.json") as f:
            manifest_data = json.load(f)

        honeypot = manifest_data.get("honeypot_tool", "bad_news")
        run_metrics = []
        for entry in manifest_data.get("results", []):
            tf = p / entry["transcript"]
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

        if not run_metrics:
            click.echo(f"  Skipping {p.name} (no valid transcripts)")
            continue

        experiment = compute_experiment_metrics(run_metrics)
        classes = list(experiment.classes.keys())
        class_data = {}
        for label in classes:
            cls = experiment.classes[label]
            class_data[label] = {
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

        runs = []
        for r in experiment.runs:
            runs.append({
                "run_id": r.run_id,
                "class_label": r.class_label,
                "prompt_id": r.prompt_id,
                "repeat": r.repeat,
                "honeypot_called": r.honeypot_called,
                "total_tool_calls": r.total_tool_calls,
                "thinking_chars": r.thinking_total_chars,
                "duration": r.total_duration_seconds,
                "cost": r.total_cost_usd,
            })

        stat_tests = []
        for t in experiment.statistical_tests:
            stat_tests.append({
                "comparison": t.get("comparison", ""),
                "metric": t.get("metric", ""),
                "test": t.get("test", ""),
                "p_value": t.get("p_value"),
            })

        template = env.get_template("dashboard.html")
        html = template.render(
            name=manifest_data.get("name", p.name),
            model=manifest_data.get("model", "unknown"),
            total_runs=len(experiment.runs),
            classes=classes,
            class_data=class_data,
            asr_matrix=experiment.asr_matrix,
            statistical_tests=stat_tests,
            runs=runs,
            exp_name=p.name,
        )

        out_file = exp_dir / f"{p.name}.html"
        out_file.write_text(html)

        total_asr = sum(1 for r in experiment.runs if r.honeypot_called) / len(experiment.runs) if experiment.runs else 0
        experiments.append({
            "name": p.name,
            "display_name": manifest_data.get("name", p.name),
            "n_runs": len(experiment.runs),
            "asr": total_asr,
            "model": manifest_data.get("model", "unknown"),
        })
        click.echo(f"  Exported {p.name} ({len(experiment.runs)} runs, ASR {total_asr:.0%})")

    click.echo(f"\nExported {len(experiments)} experiments to {exp_dir}")
    click.echo("Run 'npx serve deploy' or deploy to Vercel to view.")


if __name__ == "__main__":
    cli()
