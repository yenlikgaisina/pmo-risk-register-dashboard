"""
Generates a synthetic monthly risk register for a fictional infrastructure
programme ("Ridgemoor Grid Connection Programme"). All entities, people,
suppliers and events are invented for portfolio purposes -- this is not
real data from any organisation.

Run from the project root:
    python scripts/generate_data.py

Writes three CSVs to data/:
    risk_register.csv        one row per risk (static fields)
    risk_snapshots.csv       one row per risk per monthly reporting cycle
    mitigation_actions.csv   one row per mitigation action
"""

import random
from datetime import date, timedelta

import numpy as np
import pandas as pd

RNG_SEED = 42
random.seed(RNG_SEED)
np.random.seed(RNG_SEED)

REPORT_MONTHS = pd.date_range("2026-01-31", periods=6, freq="ME")  # Jan-Jun 2026

CATEGORIES = {
    "Supplier & Delivery": [
        "Key steel fabrication supplier delivery slippage",
        "Single-source component supplier capacity constraint",
        "Sub-contractor mobilisation delay on site enabling works",
        "Long-lead electrical switchgear delivery risk",
        "Supplier quality non-conformance on structural modules",
        "Logistics and customs delay for imported components",
    ],
    "Cost & Commercial": [
        "Steel and raw material price inflation",
        "Foreign exchange exposure on imported plant",
        "Contract variation cost growth on civils package",
        "Underestimated waste and disposal cost allowance",
        "Insurance premium increase at policy renewal",
        "Commercial dispute with tier-1 contractor over scope",
    ],
    "Engineering & Design Change": [
        "Late-stage design change to foundation specification",
        "Interface misalignment between mechanical and electrical packages",
        "Design change driven by updated ground-condition survey",
        "Unresolved technical query blocking construction drawings",
        "Configuration control gap between design revisions",
    ],
    "Schedule & Programme": [
        "Critical path slippage on site enabling works",
        "Concurrent workstream congestion on site",
        "Weather-related delay to outdoor construction activities",
        "Delayed handover from design to construction phase",
        "Programme float erosion across multiple packages",
    ],
    "Regulatory & Consents": [
        "Delay in planning consent determination",
        "Environmental permit variation required",
        "Regulator information request extending review period",
        "Change in regulatory guidance affecting design basis",
        "Statutory consultee objection requiring design amendment",
    ],
    "Resourcing & Capability": [
        "Shortage of specialist commissioning engineers",
        "Key-person dependency in project controls team",
        "Contractor resourcing shortfall during peak construction",
        "Skills gap in an emerging technology area",
        "Staff turnover in a stakeholder-facing PMO role",
    ],
    "Health & Safety": [
        "Elevated risk during high-value lifting operations",
        "Confined-space entry procedure non-compliance",
        "Site traffic management risk during peak deliveries",
        "Working-at-height control gap on scaffold access",
        "Lone-working risk during remote inspection activities",
    ],
}

OWNERS_BY_CATEGORY = {
    "Supplier & Delivery": ["Supply Chain Lead", "Procurement Manager"],
    "Cost & Commercial": ["Commercial Manager", "Cost Manager"],
    "Engineering & Design Change": ["Design Manager", "Principal Engineer"],
    "Schedule & Programme": ["Programme Scheduler", "Project Controls Manager"],
    "Regulatory & Consents": ["Regulatory & Consents Manager"],
    "Resourcing & Capability": ["Resourcing Manager", "PMO Lead"],
    "Health & Safety": ["HSE Manager", "Construction Manager"],
}

MITIGATION_TEMPLATES = [
    "Escalate to supplier/contractor governance board",
    "Agree revised delivery milestone with contingency",
    "Commission independent technical review",
    "Increase inspection and audit frequency",
    "Secure alternative source or dual-sourcing option",
    "Update risk-adjusted cost and schedule baseline",
    "Raise formal query with regulator/consultee",
    "Backfill role with contract resource",
    "Implement additional site control / toolbox talk",
    "Bring forward long-lead procurement decision",
]

STATUS_FLOW_NOTE = (
    "Status reflects the review at each monthly cut-off, not a live feed."
)


def business_day_offset(start: date, days: int) -> date:
    return start + timedelta(days=days)


def build_risk_register() -> pd.DataFrame:
    rows = []
    risk_id = 1
    programme_start = date(2025, 9, 1)
    for category, titles in CATEGORIES.items():
        for title in titles:
            rid = f"R{risk_id:03d}"
            owner = random.choice(OWNERS_BY_CATEGORY[category])
            # Stagger when each risk was first raised across the programme,
            # including some raised partway through the reporting window so
            # ageing has real spread rather than everything being long-lived.
            days_after_start = random.randint(0, 290)
            date_raised = business_day_offset(programme_start, days_after_start)
            # Baseline (inherent) probability/impact set when the risk was raised
            base_prob = random.choices([1, 2, 3, 4, 5], weights=[5, 20, 35, 28, 12])[0]
            base_impact = random.choices([1, 2, 3, 4, 5], weights=[5, 15, 30, 32, 18])[0]
            rows.append(
                {
                    "risk_id": rid,
                    "category": category,
                    "title": title,
                    "owner": owner,
                    "date_raised": date_raised,
                    "inherent_probability": base_prob,
                    "inherent_impact": base_impact,
                }
            )
            risk_id += 1
    return pd.DataFrame(rows)


def simulate_snapshots(register: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    snapshot_rows = []
    action_rows = []
    action_id = 1

    for _, risk in register.iterrows():
        rid = risk["risk_id"]
        prob = risk["inherent_probability"]
        impact = risk["inherent_impact"]
        date_raised = risk["date_raised"]

        # Each risk gets a mitigation "drift": most trend down as actions land,
        # a minority (emerging risks) trend up, a few stay flat.
        drift_type = random.choices(
            ["improving", "emerging", "flat", "volatile"],
            weights=[45, 20, 20, 15],
        )[0]

        closed_from_month = None
        if drift_type == "improving" and random.random() < 0.35:
            # Some well-managed risks close out partway through the programme
            closed_from_month = random.randint(2, 5)

        residual_prob, residual_impact = prob, impact

        for m_idx, month_end in enumerate(REPORT_MONTHS):
            month_end_date = month_end.date()
            if month_end_date < date_raised:
                continue  # risk didn't exist yet at this reporting cut-off

            if closed_from_month is not None and m_idx >= closed_from_month:
                status = "Closed"
            else:
                status = "Open"

            if status == "Open":
                if drift_type == "improving":
                    residual_prob = max(1, residual_prob - random.choice([0, 0, 1]))
                    residual_impact = max(1, residual_impact - random.choice([0, 0, 1]))
                elif drift_type == "emerging":
                    residual_prob = min(5, residual_prob + random.choice([0, 0, 1]))
                    residual_impact = min(5, residual_impact + random.choice([0, 1]))
                elif drift_type == "volatile":
                    residual_prob = min(5, max(1, residual_prob + random.choice([-1, 0, 1])))
                    residual_impact = min(5, max(1, residual_impact + random.choice([-1, 0, 1])))
                # "flat" -> no change

            residual_score = residual_prob * residual_impact
            inherent_score = prob * impact

            review_date = month_end_date
            days_open = (review_date - date_raised).days

            snapshot_rows.append(
                {
                    "risk_id": rid,
                    "report_month": month_end_date.strftime("%Y-%m"),
                    "review_date": review_date,
                    "status": status,
                    "residual_probability": residual_prob,
                    "residual_impact": residual_impact,
                    "residual_score": residual_score,
                    "inherent_score": inherent_score,
                    "days_open": days_open,
                }
            )

            # Generate 0-2 mitigation actions per risk per month while open
            if status == "Open" and random.random() < 0.55:
                n_actions = random.choice([1, 1, 2])
                for _ in range(n_actions):
                    due_offset = random.randint(7, 45)
                    due_date = month_end_date + timedelta(days=due_offset)
                    # Whether the action is overdue is evaluated against the
                    # programme's latest reporting cut-off (end of dataset)
                    is_latest = month_end == REPORT_MONTHS[-1]
                    if is_latest:
                        action_status = random.choices(
                            ["Open", "Overdue", "Complete"], weights=[45, 25, 30]
                        )[0]
                    else:
                        action_status = random.choices(
                            ["Complete", "Open"], weights=[70, 30]
                        )[0]
                    action_rows.append(
                        {
                            "action_id": f"A{action_id:04d}",
                            "risk_id": rid,
                            "report_month": month_end_date.strftime("%Y-%m"),
                            "action": random.choice(MITIGATION_TEMPLATES),
                            "owner": risk["owner"],
                            "due_date": due_date,
                            "status": action_status,
                        }
                    )
                    action_id += 1

    return pd.DataFrame(snapshot_rows), pd.DataFrame(action_rows)


def main():
    register = build_risk_register()
    snapshots, actions = simulate_snapshots(register)

    register.to_csv("data/risk_register.csv", index=False)
    snapshots.to_csv("data/risk_snapshots.csv", index=False)
    actions.to_csv("data/mitigation_actions.csv", index=False)

    print(f"Risks: {len(register)}")
    print(f"Snapshot rows: {len(snapshots)}")
    print(f"Actions: {len(actions)}")
    print(STATUS_FLOW_NOTE)


if __name__ == "__main__":
    main()
