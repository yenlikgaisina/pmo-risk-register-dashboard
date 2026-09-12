"""
Data-quality checks for the PMO risk register dataset.

These tests validate the raw CSVs in data/ (the source of truth that
scripts/build_analysis.py and scripts/build_dashboard.py consume) rather
than the generated dashboard_data.json, so a bad data change is caught
before it ever reaches the dashboard.

Run with:
    pytest
"""

from pathlib import Path

import pandas as pd
import pytest

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

VALID_ACTION_STATUSES = {"Open", "Complete", "Overdue"}
VALID_RISK_STATUSES = {"Open", "Closed"}


@pytest.fixture(scope="module")
def register():
    return pd.read_csv(DATA_DIR / "risk_register.csv")


@pytest.fixture(scope="module")
def snapshots():
    return pd.read_csv(DATA_DIR / "risk_snapshots.csv")


@pytest.fixture(scope="module")
def actions():
    return pd.read_csv(DATA_DIR / "mitigation_actions.csv")


# --- risk_id is unique -------------------------------------------------


def test_risk_id_is_unique(register):
    duplicates = register["risk_id"][register["risk_id"].duplicated()].tolist()
    assert register["risk_id"].is_unique, f"Duplicate risk_id values found: {duplicates}"


def test_risk_id_not_null(register):
    assert register["risk_id"].notna().all()
    assert (register["risk_id"].str.strip() != "").all()


# --- probability is between 1 and 5 -------------------------------------


def test_inherent_probability_in_range(register):
    assert register["inherent_probability"].between(1, 5).all(), (
        "inherent_probability values out of the 1-5 range: "
        f"{register.loc[~register['inherent_probability'].between(1, 5), 'inherent_probability'].tolist()}"
    )


def test_residual_probability_in_range(snapshots):
    assert snapshots["residual_probability"].between(1, 5).all(), (
        "residual_probability values out of the 1-5 range: "
        f"{snapshots.loc[~snapshots['residual_probability'].between(1, 5), 'residual_probability'].tolist()}"
    )


# --- impact is between 1 and 5 ------------------------------------------


def test_inherent_impact_in_range(register):
    assert register["inherent_impact"].between(1, 5).all(), (
        "inherent_impact values out of the 1-5 range: "
        f"{register.loc[~register['inherent_impact'].between(1, 5), 'inherent_impact'].tolist()}"
    )


def test_residual_impact_in_range(snapshots):
    assert snapshots["residual_impact"].between(1, 5).all(), (
        "residual_impact values out of the 1-5 range: "
        f"{snapshots.loc[~snapshots['residual_impact'].between(1, 5), 'residual_impact'].tolist()}"
    )


# --- score = probability x impact ---------------------------------------


def test_residual_score_equals_probability_times_impact(snapshots):
    expected = snapshots["residual_probability"] * snapshots["residual_impact"]
    mismatches = snapshots.loc[expected != snapshots["residual_score"]]
    assert mismatches.empty, (
        "residual_score does not equal residual_probability x residual_impact for rows:\n"
        f"{mismatches[['risk_id', 'report_month', 'residual_probability', 'residual_impact', 'residual_score']]}"
    )


def test_inherent_score_equals_probability_times_impact(register, snapshots):
    merged = snapshots.merge(
        register[["risk_id", "inherent_probability", "inherent_impact"]],
        on="risk_id",
        how="left",
    )
    expected = merged["inherent_probability"] * merged["inherent_impact"]
    mismatches = merged.loc[expected != merged["inherent_score"]]
    assert mismatches.empty, (
        "inherent_score does not equal inherent_probability x inherent_impact for rows:\n"
        f"{mismatches[['risk_id', 'report_month', 'inherent_probability', 'inherent_impact', 'inherent_score']]}"
    )


# --- all mitigation actions reference a valid risk_id --------------------


def test_mitigation_actions_reference_valid_risk_id(register, actions):
    valid_ids = set(register["risk_id"])
    orphaned = sorted(set(actions["risk_id"]) - valid_ids)
    assert not orphaned, f"mitigation_actions.csv references unknown risk_id values: {orphaned}"


def test_risk_snapshots_reference_valid_risk_id(register, snapshots):
    valid_ids = set(register["risk_id"])
    orphaned = sorted(set(snapshots["risk_id"]) - valid_ids)
    assert not orphaned, f"risk_snapshots.csv references unknown risk_id values: {orphaned}"


# --- dates parse correctly -----------------------------------------------


def test_date_raised_parses(register):
    parsed = pd.to_datetime(register["date_raised"], format="%Y-%m-%d", errors="coerce")
    bad_rows = register.loc[parsed.isna(), "risk_id"].tolist()
    assert parsed.notna().all(), f"date_raised failed to parse for risk_id(s): {bad_rows}"


def test_due_date_parses(actions):
    parsed = pd.to_datetime(actions["due_date"], format="%Y-%m-%d", errors="coerce")
    bad_rows = actions.loc[parsed.isna(), "action_id"].tolist()
    assert parsed.notna().all(), f"due_date failed to parse for action_id(s): {bad_rows}"


def test_review_date_parses(snapshots):
    parsed = pd.to_datetime(snapshots["review_date"], format="%Y-%m-%d", errors="coerce")
    bad_rows = snapshots.loc[parsed.isna(), "risk_id"].tolist()
    assert parsed.notna().all(), f"review_date failed to parse for risk_id(s): {bad_rows}"


# --- status values are valid ----------------------------------------------


def test_mitigation_action_status_is_valid(actions):
    invalid = sorted(set(actions["status"]) - VALID_ACTION_STATUSES)
    assert not invalid, (
        f"mitigation_actions.csv has unexpected status value(s): {invalid} "
        f"(expected one of {sorted(VALID_ACTION_STATUSES)})"
    )


def test_risk_snapshot_status_is_valid(snapshots):
    invalid = sorted(set(snapshots["status"]) - VALID_RISK_STATUSES)
    assert not invalid, (
        f"risk_snapshots.csv has unexpected status value(s): {invalid} "
        f"(expected one of {sorted(VALID_RISK_STATUSES)})"
    )
