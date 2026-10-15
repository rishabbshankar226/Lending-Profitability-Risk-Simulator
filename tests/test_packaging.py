"""The published wheel must run its default CLI outside the source checkout."""

import json
import os
import subprocess
import sys
from pathlib import Path


def test_installed_wheel_cli_contains_its_default_dataset(tmp_path):
    root = Path(__file__).resolve().parents[1]
    wheels = tmp_path / "wheels"
    built = subprocess.run(
        [sys.executable, "-m", "pip", "wheel", "--no-deps", "--wheel-dir", str(wheels), str(root)],
        cwd=tmp_path, capture_output=True, text=True, timeout=120, check=False,
    )
    assert built.returncode == 0, built.stderr
    candidates = list(wheels.glob("lending_profitability_risk_simulator-*.whl"))
    assert len(candidates) == 1
    installed = tmp_path / "installed"
    copied = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-deps", "--no-compile", "--target", str(installed), str(candidates[0])],
        cwd=tmp_path, capture_output=True, text=True, timeout=30, check=False,
    )
    assert copied.returncode == 0, copied.stderr
    output = tmp_path / "result"
    executed = subprocess.run(
        [sys.executable, "-P", "-m", "lending_simulator.cli", "--output", str(output)],
        cwd=tmp_path, env={**os.environ, "PYTHONPATH": str(installed)},
        capture_output=True, text=True, timeout=30, check=False,
    )
    assert executed.returncode == 0, executed.stderr
    result = json.loads((output / "comparison.json").read_text())
    manifest = json.loads((root / "data/manifest.json").read_text())
    assert result["dataset"]["dataset_hash"] == manifest["dataset_hash"]
    assert result["decision"]["recommended_policy"] == "conservative"
    assert len(result["policies"]) == 3
