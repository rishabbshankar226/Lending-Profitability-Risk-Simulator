import json
import subprocess
import sys
from pathlib import Path

import pytest


def test_cli_produces_reproducible_manifests_and_policy_outputs(tmp_path):
    root = Path(__file__).resolve().parents[1]
    completed = subprocess.run([sys.executable, "-m", "lending_simulator.cli", "--output", str(tmp_path)],
                               cwd=root, capture_output=True, text=True, timeout=30)
    assert completed.returncode == 0, completed.stderr
    summary = json.loads((tmp_path / "comparison.json").read_text())
    assert summary["decision"]["recommended_policy"] == "conservative"
    assert len(summary["policies"]) == 3
    assert all(p["checks"]["passed"] for p in summary["policies"])
    for policy in ("conservative", "balanced", "aggressive"):
        assert (tmp_path / f"{policy}.zip").is_file()
        assert (tmp_path / f"{policy}.xlsx").is_file()


@pytest.mark.parametrize('row', ['syn-a,0,low,10000,ignored\n', 'syn-a,0,low,"10000\n'])
def test_cli_rejects_malformed_csv_without_overwriting_outputs(tmp_path, row):
    source = tmp_path / 'applications.csv'
    source.write_text('application_id,month,risk_band,principal_cents\n' + row)
    output = tmp_path / 'outputs'
    output.mkdir()
    existing = output / 'comparison.json'
    existing.write_text('Existing comparison')
    completed = subprocess.run([sys.executable, '-m', 'lending_simulator.cli',
                                '--dataset', str(source), '--output', str(output)],
                               capture_output=True, text=True, timeout=30)
    assert completed.returncode == 2
    assert 'CSV' in completed.stderr
    assert 'Traceback' not in completed.stderr
    assert existing.read_text() == 'Existing comparison'
    assert list(output.iterdir()) == [existing]
