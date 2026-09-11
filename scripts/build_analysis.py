"""
Reads the synthetic risk register CSVs and produces:
  - static PNG charts in assets/ (used in the README / notebook)
  - data/dashboard_data.json, the single data file the HTML dashboard reads

Run after generate_data.py:
    python scripts/build_analysis.py
"""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "font.size": 10,
    }
)

REGISTER = pd.read_csv("data/risk_register.csv", parse_dates=["date_raised"])
SNAPSHOTS = pd.read_csv("data/risk_snapshots.csv", parse_dates=["review_date"])
ACTIONS = pd.read_csv("data/mitigation_actions.csv", parse_dates=["due_date"])

MONTHS = sorted(SNAPSHOTS["report_month"].unique())
LATEST_MONTH = MONTHS[-1]
PREV_MONTH = MONTHS[-2]


def latest_snapshot(month):
    return SNAPSHOTS[SNAPSHOTS["report_month"] == month]


def current_view():
    latest = latest_snapshot(LATEST_MONTH)
    merged = latest.merge(REGISTER, on="risk_id", how="left")
    return merged


def heatmap_matrix(df, prob_col, impact_col):
    matrix = np.zeros((5, 5), dtype=int)
    for _, row in df.iterrows():
        p = int(row[prob_col]) - 1
        i = int(row[impact_col]) - 1
        matrix[p, i] += 1
    return matrix


def save_heatmap(matrix, title, filename):
    fig, ax = plt.subplots(figsize=(4.8, 4.2))
    cmap = plt.cm.get_cmap("YlOrRd")
    im = ax.imshow(matrix, cmap=cmap, origin="lower")
    ax.set_xticks(range(5))
    ax.set_xticklabels(range(1, 6))
    ax.set_yticks(range(5))
    ax.set_yticklabels(range(1, 6))
    ax.set_xlabel("Impact")
    ax.set_ylabel("Probability")
    ax.set_title(title)
    for p in range(5):
        for i in range(5):
            val = matrix[p, i]
            if val:
                ax.text(i, p, str(val), ha="center", va="center", fontsize=9)
    fig.colorbar(im, ax=ax, shrink=0.8, label="Number of risks")
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def build_heatmaps(cur):
    open_cur = cur[cur["status"] == "Open"]
    inherent_matrix = heatmap_matrix(open_cur, "inherent_probability", "inherent_impact")
    residual_matrix = heatmap_matrix(open_cur, "residual_probability", "residual_impact")
    save_heatmap(inherent_matrix, "Inherent risk (open risks, current)", "assets/heatmap_inherent.png")
    save_heatmap(residual_matrix, "Residual risk (open risks, current)", "assets/heatmap_residual.png")
    return inherent_matrix.tolist(), residual_matrix.tolist()


def build_category_chart(cur):
    open_cur = cur[cur["status"] == "Open"]
    summary = (
        open_cur.groupby("category")
        .agg(count=("risk_id", "count"), avg_residual=("residual_score", "mean"))
        .reset_index()
        .sort_values("avg_residual", ascending=False)
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(summary["category"], summary["avg_residual"], color="#b5533c")
    ax.set_xlabel("Average residual score (open risks)")
    ax.invert_yaxis()
    for bar, count in zip(bars, summary["count"]):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f"{count} open", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig("assets/category_breakdown.png", dpi=150)
    plt.close(fig)
    return summary.to_dict(orient="records")


def build_ageing_chart(cur):
    open_cur = cur[cur["status"] == "Open"]
    bins = [0, 30, 60, 90, 120, 180, 10000]
    labels = ["0-30", "31-60", "61-90", "91-120", "121-180", "180+"]
    open_cur = open_cur.copy()
    open_cur["age_band"] = pd.cut(open_cur["days_open"], bins=bins, labels=labels, right=True)
    ageing = open_cur["age_band"].value_counts().reindex(labels).fillna(0).astype(int)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(ageing.index.astype(str), ageing.values, color="#3c6e91")
    ax.set_xlabel("Days open")
    ax.set_ylabel("Number of open risks")
    ax.set_title("Risk ageing (days since raised)")
    fig.tight_layout()
    fig.savefig("assets/risk_ageing.png", dpi=150)
    plt.close(fig)
    return {"labels": labels, "counts": ageing.values.tolist()}


def build_trend_chart():
    trend = (
        SNAPSHOTS[SNAPSHOTS["status"] == "Open"]
        .groupby("report_month")
        .agg(open_risks=("risk_id", "count"), total_residual=("residual_score", "sum"),
             avg_residual=("residual_score", "mean"))
        .reindex(MONTHS)
        .reset_index()
    )
    fig, ax1 = plt.subplots(figsize=(7, 4))
    ax1.plot(trend["report_month"], trend["open_risks"], marker="o", color="#3c6e91", label="Open risks")
    ax1.set_ylabel("Open risks", color="#3c6e91")
    ax2 = ax1.twinx()
    ax2.plot(trend["report_month"], trend["avg_residual"], marker="s", color="#b5533c", label="Avg residual score")
    ax2.set_ylabel("Avg residual score", color="#b5533c")
    ax1.set_title("Month-on-month risk movement")
    fig.tight_layout()
    fig.savefig("assets/trend_movement.png", dpi=150)
    plt.close(fig)
    return trend.to_dict(orient="records")


def emerging_risks(cur):
    prev = latest_snapshot(PREV_MONTH)[["risk_id", "residual_score"]].rename(
        columns={"residual_score": "prev_residual_score"}
    )
    merged = cur.merge(prev, on="risk_id", how="left")
    merged["prev_residual_score"] = merged["prev_residual_score"].fillna(merged["residual_score"])
    merged["movement"] = merged["residual_score"] - merged["prev_residual_score"]
    emerging = merged[(merged["status"] == "Open") & (merged["movement"] > 0)].sort_values(
        "movement", ascending=False
    )
    return emerging[
        ["risk_id", "title", "category", "owner", "prev_residual_score", "residual_score", "movement"]
    ].head(10).to_dict(orient="records")


def top_risks(cur):
    open_cur = cur[cur["status"] == "Open"].sort_values("residual_score", ascending=False)
    return open_cur[
        ["risk_id", "title", "category", "owner", "residual_probability", "residual_impact",
         "residual_score", "days_open"]
    ].head(10).to_dict(orient="records")


def overdue_actions():
    latest_actions = ACTIONS[ACTIONS["report_month"] == LATEST_MONTH]
    overdue = latest_actions[latest_actions["status"] == "Overdue"]
    merged = overdue.merge(REGISTER[["risk_id", "title", "category"]], on="risk_id", how="left")
    merged = merged.copy()
    merged["due_date"] = pd.to_datetime(merged["due_date"]).dt.strftime("%Y-%m-%d")
    return merged[["action_id", "risk_id", "title", "category", "action", "owner", "due_date"]].to_dict(
        orient="records"
    )


def kpis(cur, overdue_list, emerging_list, trend):
    open_cur = cur[cur["status"] == "Open"]
    closed_cur = cur[cur["status"] == "Closed"]
    return {
        "total_risks": int(len(cur)),
        "open_risks": int(len(open_cur)),
        "closed_risks": int(len(closed_cur)),
        "high_residual_risks": int((open_cur["residual_score"] >= 15).sum()),
        "overdue_actions": len(overdue_list),
        "emerging_risks": len(emerging_list),
        "avg_residual_score": round(float(open_cur["residual_score"].mean()), 2),
        "latest_month": LATEST_MONTH,
    }


def main():
    cur = current_view()
    inherent_matrix, residual_matrix = build_heatmaps(cur)
    category_summary = build_category_chart(cur)
    ageing = build_ageing_chart(cur)
    trend = build_trend_chart()
    emerging_list = emerging_risks(cur)
    top_risk_list = top_risks(cur)
    overdue_list = overdue_actions()
    kpi_block = kpis(cur, overdue_list, emerging_list, trend)

    open_cur = cur[cur["status"] == "Open"].copy()
    risk_records = open_cur[
        [
            "risk_id", "title", "category", "owner", "date_raised",
            "inherent_probability", "inherent_impact", "inherent_score",
            "residual_probability", "residual_impact", "residual_score", "days_open",
        ]
    ].copy()
    risk_records["date_raised"] = risk_records["date_raised"].dt.strftime("%Y-%m-%d")

    dashboard_data = {
        "kpis": kpi_block,
        "heatmap": {"inherent": inherent_matrix, "residual": residual_matrix},
        "category_summary": category_summary,
        "ageing": ageing,
        "trend": trend,
        "emerging_risks": emerging_list,
        "top_risks": top_risk_list,
        "overdue_actions": overdue_list,
        "risks": risk_records.to_dict(orient="records"),
        "months": MONTHS,
    }

    with open("data/dashboard_data.json", "w") as f:
        json.dump(dashboard_data, f, indent=2, default=str)

    print("KPIs:", kpi_block)
    print(f"Emerging risks flagged: {len(emerging_list)}")
    print(f"Overdue actions: {len(overdue_list)}")
    print("Wrote data/dashboard_data.json and assets/*.png")


if __name__ == "__main__":
    main()
