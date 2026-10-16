"""Independent domain, reproducibility and exact-intake regressions."""

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from decimal import ROUND_CEILING, ROUND_FLOOR, Inexact, localcontext
from decimal import Decimal as D
from random import getstate

import pytest

from lending_simulator.cli import main
from lending_simulator.data import generate_dataset, save_dataset
from lending_simulator.decisions import compare_policies, select_strategy
from lending_simulator.model import contractual_payment, monthly_hazard
from lending_simulator.presentation import band_curves, cohort_heatmap
from lending_simulator.types import Assumptions
from lending_simulator.ui.data import profit_bridge
from lending_simulator.ui.formatting import assumption_value, money, percent, points
from lending_simulator.ui.state import controls_for, parse_controls


@pytest.mark.parametrize("probability", [D("-.01"), D("1.01"), D("NaN"), D("Infinity"), True, 0.1])
def test_hazard_rejects_invalid_pd_before_arithmetic(probability):
    with pytest.raises(ValueError):
        monthly_hazard(probability, 12)


@pytest.mark.parametrize("term", [0, -1, True, D(12), 1.5])
def test_financial_helpers_require_a_positive_integer_term(term):
    with pytest.raises(ValueError):
        monthly_hazard(D(".02"), term)
    with pytest.raises(ValueError):
        contractual_payment(D(1200), D(".12"), term)


@pytest.mark.parametrize("principal,rate", [
    (D(-1), D(".12")), (D("NaN"), D(".12")),
    (D(1200), D("-.01")), (D(1200), D("1.01")),
    (True, D(".12")), (D(1200), .12),
])
def test_payment_rejects_invalid_exposure_and_rate(principal, rate):
    with pytest.raises(ValueError):
        contractual_payment(principal, rate, 12)


def test_small_positive_pd_does_not_disappear_through_subtraction():
    pd = D("1e-40")
    with localcontext() as ctx:
        ctx.prec = 100
        expected = 1 - (1 - pd) ** (D(1) / 12)
    observed = monthly_hazard(pd, 12)
    assert observed > 0
    with localcontext() as ctx:
        ctx.prec = 100
        assert abs(observed / expected - 1) < D("1e-30")


def test_small_positive_rate_has_a_finite_payment():
    with localcontext() as ctx:
        ctx.prec = 100
        rate = D("1e-40") / 12
        expected = D(1200) * rate / (1 - (1 + rate) ** -12)
    observed = contractual_payment(D(1200), D("1e-40"), 12)
    assert observed.is_finite()
    with localcontext() as ctx:
        ctx.prec = 100
        assert abs(observed - expected) < D("1e-30")


@pytest.mark.parametrize("rounding,trap", [(ROUND_FLOOR, False), (ROUND_CEILING, False), (ROUND_CEILING, True)])
def test_model_results_and_ids_do_not_depend_on_ambient_decimal_state(rounding, trap):
    dataset = generate_dataset(seed=881, count=48)
    baseline = compare_policies(dataset, Assumptions())
    with localcontext() as ctx:
        ctx.prec = 6
        ctx.rounding = rounding
        ctx.traps[Inexact] = trap
        observed = compare_policies(dataset, Assumptions())
    assert observed == baseline


def test_policy_order_uses_every_unrounded_profit_digit():
    first, _, last = compare_policies(generate_dataset(count=48), Assumptions())
    assumptions = replace(Assumptions(), loss_cap=D(1), cash_floor=D(0))
    lower = replace(first, assumptions=assumptions, summary=replace(first.summary,
        operating_result=D(1), loss_ratio=D(".01"), minimum_cash=D(1)))
    higher = replace(last, assumptions=assumptions, summary=replace(last.summary,
        operating_result=D("1.0000000000000000000000000000000001"),
        loss_ratio=D(".02"), minimum_cash=D(1)))
    assert select_strategy((lower, higher)).recommended_policy == "aggressive"


def test_profit_bridge_negation_does_not_round_its_captured_values():
    result = compare_policies(generate_dataset(count=48), Assumptions())[1]
    with localcontext() as ctx:
        ctx.prec = 6
        observed = profit_bridge(result)
    assert dict(observed)["Funding"] == result.summary.funding_expense.copy_negate()


@pytest.mark.parametrize("payload", ["null", "[]", '"text"', '{"assumptions": null}', '{"assumptions": []}'])
def test_cli_invalid_json_shapes_return_a_clean_failure_without_output(tmp_path, payload, capsys):
    path = tmp_path / "invalid.json"
    path.write_text(payload)
    output = tmp_path / "output"
    assert main(["--assumptions", str(path), "--output", str(output)]) == 2
    assert "Scenario failed:" in capsys.readouterr().err
    assert not output.exists()


def test_cli_preserves_the_original_decimal_json_token(tmp_path):
    path = tmp_path / "assumptions.json"
    path.write_text('{"initial_cash": 10000000000000000.01}')
    dataset_path = tmp_path / "applications.csv"
    save_dataset(generate_dataset(count=24), dataset_path)
    output = tmp_path / "output"
    assert main(["--dataset", str(dataset_path), "--assumptions", str(path), "--output", str(output)]) == 0
    result = json.loads((output / "comparison.json").read_text())
    assert result["policies"][0]["assumptions"]["initial_cash"] == "10000000000000000.01"


def test_synthetic_generation_does_not_touch_global_random_state():
    before = getstate()
    assert generate_dataset(seed=331, count=72) == generate_dataset(seed=331, count=72)
    assert getstate() == before


def test_presentation_and_draft_calculations_ignore_ambient_rounding_and_traps():
    from pandas.testing import assert_frame_equal
    result = compare_policies(generate_dataset(count=48), Assumptions())[1]
    curves, cohorts = band_curves(result), cohort_heatmap(result)
    controls = controls_for(Assumptions())
    with localcontext() as ctx:
        ctx.prec = 6
        ctx.rounding = ROUND_CEILING
        ctx.traps[Inexact] = True
        assert_frame_equal(band_curves(result), curves)
        assert_frame_equal(cohort_heatmap(result), cohorts)
        assert controls_for(Assumptions()) == controls
        assert parse_controls(controls) == Assumptions()
        assert assumption_value("monthly_opex", D("7500.012345")) == "$7,500.012345"
        assert money(D("1250.5")) == "$1,250"


@pytest.mark.parametrize("value", [D("Infinity"), D("-Infinity"), float("inf"), float("-inf")])
def test_report_labels_do_not_propagate_infinity(value):
    assert money(value) == "Unavailable"
    assert percent(value) == "Unavailable"
    assert points(value) == "Unavailable"


@pytest.mark.parametrize("sign,expected", [("", "<$1"), ("-", "(<$1)")])
def test_money_labels_keep_exact_values_below_reporting_threshold(sign, expected):
    assert money(D(sign + "0." + "9" * 110)) == expected


@pytest.mark.parametrize("sign,expected", [("", "<0.01 pp"), ("-", "−<0.01 pp")])
def test_point_labels_keep_exact_values_below_reporting_threshold(sign, expected):
    assert points(D(sign + "0.00" + "9" * 110)) == expected


@pytest.mark.parametrize("sign", ["", "-"])
def test_money_labels_preserve_large_integer_dollars(sign):
    digits = "1" + "0" * 95 + "1"
    amount = f"{int(digits):,}"
    expected = f"(${amount})" if sign else f"${amount}"
    assert money(D(sign + digits)) == expected


@pytest.mark.parametrize("payload", [
    '{"initial_cash": 1, "initial_cash": 2}',
    '{"initial_cash": NaN}', '{"initial_cash": Infinity}',
    '{"initial_cash": true}',
    '{"metadata": ' + '[' * 129 + '0' + ']' * 129 + '}',
])
def test_cli_rejects_ambiguous_or_nonfinite_json(tmp_path, payload, capsys):
    path = tmp_path / "invalid.json"
    path.write_text(payload)
    output = tmp_path / "output"
    assert main(["--assumptions", str(path), "--output", str(output)]) == 2
    assert "Scenario failed:" in capsys.readouterr().err
    assert not output.exists()


def test_threaded_model_runs_and_synthetic_rngs_are_isolated():
    def compute(seed):
        with localcontext() as ctx:
            ctx.prec = seed % 17 + 3
            ctx.rounding = ROUND_CEILING if seed % 2 else ROUND_FLOOR
            ctx.traps[Inexact] = True
            return compare_policies(generate_dataset(seed=seed, count=72), Assumptions())
    seeds = list(range(8))
    expected = [compare_policies(generate_dataset(seed=seed, count=72), Assumptions()) for seed in seeds]
    with ThreadPoolExecutor(max_workers=4) as executor:
        assert list(executor.map(compute, seeds)) == expected


def test_generated_pd_lgd_exposure_and_accounting_identities():
    from random import Random

    from lending_simulator.model import run_model
    from lending_simulator.types import CohortInput
    rng = Random(20261015)
    for _ in range(48):
        probability = D(rng.randrange(0, 101)) / 100
        recovery = D(rng.randrange(0, 101)) / 100
        principal = D(rng.randrange(1, 10000001)) / 100
        assumptions = replace(Assumptions(), pd_low=probability, recovery_rate=recovery,
            recovery_lag=0, monthly_opex=D(0), cash_floor=D(0))
        result = run_model((CohortInput(0, "low", D(1), principal),),
            assumptions, "conservative", D(1), "generated-identity-fixture")
        hazard = monthly_hazard(probability, 12)
        with localcontext() as ctx:
            ctx.prec = 110
            assert result.checks.passed
            assert 0 <= hazard <= 1
            for row in result.monthly:
                assert row.opening_principal >= 0
                expected_loss = row.opening_principal * hazard * (1 - recovery)
                assert abs(row.net_credit_loss - expected_loss) <= D("1e-80")
                assert abs(row.opening_principal + row.originations - row.principal_collections
                           - row.gross_chargeoffs - row.ending_principal) <= D("1e-80")
                assert abs(row.opening_debt + row.net_debt_draw - row.ending_debt) <= D("1e-80")
            assert result.monthly[-1].ending_principal == 0
            assert result.monthly[-1].ending_debt == 0


@pytest.mark.parametrize("denominator", [D("0"), D("1e-17")])
def test_count_validation_does_not_reuse_a_dollar_tolerance(denominator):
    from lending_simulator.model import run_model
    from lending_simulator.types import CohortInput
    cohort = CohortInput(0, "low", D("2e-17"), D("1e-14"))
    with pytest.raises(ValueError, match="count|application"):
        run_model((cohort,), Assumptions(), "conservative", denominator, "tiny-count-fixture")


@pytest.mark.parametrize("growth", [D(".1234567891234567"), D("-.1234567891234567"), D(".9")])
def test_growth_weighted_approval_ratios_stay_within_probability_bounds(growth):
    results = compare_policies(generate_dataset(count=200), replace(Assumptions(), demand_growth=growth))
    assert all(result.checks.passed for result in results)
    assert all(0 <= result.summary.approval_rate <= 1 for result in results)


def test_count_roundoff_cannot_report_more_than_full_approval():
    from lending_simulator.model import run_model
    from lending_simulator.types import CohortInput
    count = D("1." + "0" * 94 + "1")
    cohort = CohortInput(0, "low", count, D("1200"))
    result = run_model((cohort,), Assumptions(), "conservative", D("1"), "count-ulp-fixture")
    assert result.summary.approval_rate == 1
