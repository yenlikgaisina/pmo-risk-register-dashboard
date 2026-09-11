"""
Builds the single self-contained dashboard.html file from data/dashboard_data.json.
Run after build_analysis.py:
    python scripts/build_dashboard.py
"""

import json

with open("data/dashboard_data.json") as f:
    DATA = json.load(f)

DATA_JSON = json.dumps(DATA)

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Ridgemoor Grid Connection Programme — Risk Dashboard</title>
<style>
  :root {
    --bg: #f7f3ec;
    --panel: #ffffff;
    --ink: #2e2b26;
    --muted: #6b6459;
    --line: #e4ddd0;
    --terracotta: #b5533c;
    --teal: #3c6e91;
    --olive: #7c8c5a;
    --amber: #c98a2c;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    padding: 24px 16px 60px;
  }
  .wrap { max-width: 1180px; margin: 0 auto; }
  header { margin-bottom: 24px; }
  header h1 { font-size: 1.5rem; margin: 0 0 4px; }
  header p.sub { color: var(--muted); margin: 0 0 6px; font-size: 0.92rem; }
  .disclosure {
    background: #fbf3e7;
    border: 1px solid #ecd9b8;
    color: #6b5228;
    font-size: 0.82rem;
    padding: 8px 12px;
    border-radius: 6px;
    display: inline-block;
    margin-top: 6px;
  }
  .kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin: 20px 0 28px;
  }
  .kpi {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 14px 16px;
  }
  .kpi .num { font-size: 1.6rem; font-weight: 600; line-height: 1.1; }
  .kpi .label { font-size: 0.78rem; color: var(--muted); margin-top: 4px; }
  .kpi.warn .num { color: var(--terracotta); }
  .kpi.info .num { color: var(--teal); }

  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 24px;
  }
  @media (max-width: 820px) {
    .grid-2 { grid-template-columns: 1fr; }
  }
  .panel {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 16px;
  }
  .panel h2 { font-size: 1.02rem; margin: 0 0 10px; }
  .panel p.note { color: var(--muted); font-size: 0.8rem; margin: 8px 0 0; }

  select {
    font-size: 0.85rem;
    padding: 5px 8px;
    border-radius: 6px;
    border: 1px solid var(--line);
    background: #fff;
    color: var(--ink);
  }
  .controls { margin-bottom: 16px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
  .controls label { font-size: 0.82rem; color: var(--muted); }

  table { width: 100%; border-collapse: collapse; font-size: 0.83rem; }
  th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--line); vertical-align: top; }
  th { color: var(--muted); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.02em; }
  tr:last-child td { border-bottom: none; }
  .score-pill {
    display: inline-block;
    padding: 1px 8px;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.78rem;
    color: #fff;
  }

  .heatmap-wrap { display: flex; gap: 24px; flex-wrap: wrap; align-items: flex-start; }
  .heatmap { border-collapse: collapse; }
  .heatmap th { text-align: center; font-size: 0.7rem; color: var(--muted); padding: 3px; }
  .heatmap td {
    width: 38px; height: 34px;
    text-align: center; vertical-align: middle;
    font-size: 0.78rem; font-weight: 600;
    border: 1px solid #fff;
    color: #2e2b26;
  }
  .heatmap .axis-label { font-size: 0.72rem; color: var(--muted); }

  .chart-box { width: 100%; }
  .chart-box svg { width: 100%; height: auto; display: block; }
  .chart-box .bar-label { font-size: 10px; fill: var(--muted); }
  .chart-box .value-label { font-size: 10px; fill: var(--ink); font-weight: 600; }
  .chart-box .axis-line { stroke: var(--line); stroke-width: 1; }
  .chart-box .cat-bar-label {
    font-size: 11px; fill: var(--ink);
  }

  .toggle-btns { display: flex; gap: 6px; margin-bottom: 10px; }
  .toggle-btns button {
    font-size: 0.78rem;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid var(--line);
    background: #fff;
    cursor: pointer;
    color: var(--muted);
  }
  .toggle-btns button.active { background: var(--ink); color: #fff; border-color: var(--ink); }

  footer { margin-top: 30px; color: var(--muted); font-size: 0.78rem; line-height: 1.5; }
  footer a { color: var(--teal); }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Ridgemoor Grid Connection Programme — Risk Register Dashboard</h1>
    <p class="sub">Reporting month: __LATEST_MONTH__ &middot; __OPEN_RISKS__ open risks across 7 categories</p>
    <div class="disclosure">Synthetic case study &mdash; Ridgemoor is a fictional programme and all data below is generated, not drawn from any real organisation. See the README for methodology.</div>
  </header>

  <div class="kpi-row" id="kpiRow"></div>

  <div class="grid-2">
    <div class="panel">
      <div class="toggle-btns">
        <button id="btnResidual" class="active">Residual risk</button>
        <button id="btnInherent">Inherent risk</button>
      </div>
      <h2 id="heatmapTitle">5&times;5 heatmap — residual risk (open, current)</h2>
      <div class="controls">
        <label for="categoryFilter">Filter this heatmap by category</label>
        <select id="categoryFilter"></select>
      </div>
      <div class="heatmap-wrap">
        <table class="heatmap" id="heatmapTable"></table>
      </div>
      <p class="note">Rows = probability (1&ndash;5, bottom to top), columns = impact (1&ndash;5, left to right). Cell shade and count = number of open risks in that cell.</p>
    </div>

    <div class="panel">
      <h2>Category breakdown (open risks)</h2>
      <div id="categoryChart" class="chart-box"></div>
      <p class="note">Bar length = average residual score of open risks in the category; label = number currently open.</p>
    </div>

    <div class="panel">
      <h2>Risk ageing</h2>
      <div id="ageingChart" class="chart-box"></div>
      <p class="note">Days elapsed since each open risk was first raised.</p>
    </div>

    <div class="panel">
      <h2>Month-on-month movement</h2>
      <div id="trendChart" class="chart-box"></div>
      <p class="note"><span style="color:#3c6e91;">&#9679;</span> Open-risk count (left axis) &nbsp; <span style="color:#b5533c;">&#9679;</span> Avg residual score (right axis)</p>
    </div>
  </div>

  <div class="grid-2">
    <div class="panel">
      <h2>Top 10 risks by residual score</h2>
      <table id="topRisksTable">
        <thead><tr><th>ID</th><th>Risk</th><th>Category</th><th>Owner</th><th>Score</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
    <div class="panel">
      <h2>Emerging risks (score increased vs previous month)</h2>
      <table id="emergingTable">
        <thead><tr><th>ID</th><th>Risk</th><th>Prev.</th><th>Now</th><th>Change</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <div class="panel" style="margin-bottom:24px;">
    <h2>Overdue mitigation actions (__OVERDUE_COUNT__)</h2>
    <table id="overdueTable">
      <thead><tr><th>Risk</th><th>Category</th><th>Action</th><th>Owner</th><th>Due date</th></tr></thead>
      <tbody></tbody>
    </table>
  </div>

  <footer>
    Built as a portfolio case study of PMO-style risk reporting: probability &times; impact scoring, inherent vs
    residual risk, ownership, mitigation actions, ageing, month-on-month movement and emerging-risk analysis.
    Data is synthetic and generated with a fixed random seed &mdash; see
    <code>scripts/generate_data.py</code> and <code>scripts/build_analysis.py</code> in the repository.
    Full write-up in the <a href="README.md">README</a>.
  </footer>
</div>

<script>
const DATA = __DATA_JSON__;

function scoreColor(score) {
  // sequential terracotta scale, 1 (low) -> 25 (high)
  const t = Math.min(1, (score - 1) / 24);
  const r = Math.round(255 - t * (255 - 181));
  const g = Math.round(243 - t * (243 - 83));
  const b = Math.round(224 - t * (224 - 60));
  return `rgb(${r},${g},${b})`;
}

function scorePillColor(score) {
  if (score >= 15) return "#b5533c";
  if (score >= 8) return "#c98a2c";
  return "#7c8c5a";
}

function renderKPIs() {
  const k = DATA.kpis;
  const items = [
    { label: "Open risks", num: k.open_risks, cls: "" },
    { label: "High residual (≥15)", num: k.high_residual_risks, cls: "warn" },
    { label: "Overdue actions", num: k.overdue_actions, cls: "warn" },
    { label: "Emerging risks", num: k.emerging_risks, cls: "warn" },
    { label: "Closed risks", num: k.closed_risks, cls: "info" },
    { label: "Avg residual score", num: k.avg_residual_score, cls: "info" },
  ];
  document.getElementById("kpiRow").innerHTML = items.map(i => `
    <div class="kpi ${i.cls}">
      <div class="num">${i.num}</div>
      <div class="label">${i.label}</div>
    </div>`).join("");
}

function populateCategoryFilter() {
  const sel = document.getElementById("categoryFilter");
  const cats = ["All categories", ...DATA.category_summary.map(c => c.category)];
  sel.innerHTML = cats.map(c => `<option value="${c}">${c}</option>`).join("");
  sel.addEventListener("change", () => {
    renderHeatmap(currentHeatmapType);
  });
}

function filteredRisks() {
  const cat = document.getElementById("categoryFilter").value;
  if (!cat || cat === "All categories") return DATA.risks;
  return DATA.risks.filter(r => r.category === cat);
}

let currentHeatmapType = "residual";

function renderHeatmap(type) {
  currentHeatmapType = type;
  document.getElementById("btnResidual").classList.toggle("active", type === "residual");
  document.getElementById("btnInherent").classList.toggle("active", type === "inherent");
  document.getElementById("heatmapTitle").textContent =
    type === "residual" ? "5×5 heatmap — residual risk (open, current)" : "5×5 heatmap — inherent risk (open, current)";

  const risks = filteredRisks();
  const matrix = Array.from({ length: 5 }, () => Array(5).fill(0));
  risks.forEach(r => {
    const p = (type === "residual" ? r.residual_probability : r.inherent_probability) - 1;
    const i = (type === "residual" ? r.residual_impact : r.inherent_impact) - 1;
    matrix[p][i] += 1;
  });

  let html = "<tr><th></th>" + [1,2,3,4,5].map(i => `<th>${i}</th>`).join("") + "</tr>";
  for (let p = 4; p >= 0; p--) {
    html += `<tr><th>${p+1}</th>`;
    for (let i = 0; i < 5; i++) {
      const count = matrix[p][i];
      const score = (p + 1) * (i + 1);
      const bg = count > 0 ? scoreColor(score) : "#f2ede3";
      html += `<td style="background:${bg}">${count > 0 ? count : ""}</td>`;
    }
    html += "</tr>";
  }
  document.getElementById("heatmapTable").innerHTML = html;
}

const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(tag, attrs) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const k in attrs) el.setAttribute(k, attrs[k]);
  return el;
}

// Horizontal bar chart: category breakdown
function renderCategoryChart() {
  const box = document.getElementById("categoryChart");
  const summary = [...DATA.category_summary].sort((a, b) => b.avg_residual - a.avg_residual);
  const W = 560, rowH = 34, padLeft = 190, padRight = 46, padTop = 6;
  const H = padTop + summary.length * rowH + 6;
  const maxVal = 25;
  const plotW = W - padLeft - padRight;

  const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}` });
  summary.forEach((s, idx) => {
    const y = padTop + idx * rowH;
    const barW = Math.max(2, (s.avg_residual / maxVal) * plotW);
    svg.appendChild(svgEl("text", { x: padLeft - 8, y: y + rowH / 2 + 4, "text-anchor": "end", class: "cat-bar-label" })).textContent = s.category;
    svg.appendChild(svgEl("rect", { x: padLeft, y: y + 6, width: plotW, height: rowH - 14, fill: "#f2ede3", rx: 3 }));
    svg.appendChild(svgEl("rect", { x: padLeft, y: y + 6, width: barW, height: rowH - 14, fill: "#b5533c", rx: 3 }));
    svg.appendChild(svgEl("text", { x: padLeft + barW + 6, y: y + rowH / 2 + 4, class: "value-label" })).textContent =
      `${s.avg_residual.toFixed(1)} · ${s.count} open`;
  });
  box.innerHTML = "";
  box.appendChild(svg);
}

// Vertical bar chart: risk ageing
function renderAgeingChart() {
  const box = document.getElementById("ageingChart");
  const labels = DATA.ageing.labels, counts = DATA.ageing.counts;
  const W = 560, H = 240, padLeft = 34, padRight = 10, padTop = 16, padBottom = 28;
  const plotW = W - padLeft - padRight, plotH = H - padTop - padBottom;
  const maxVal = Math.max(1, ...counts);
  const barGap = 14;
  const barW = (plotW - barGap * (labels.length - 1)) / labels.length;

  const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}` });
  svg.appendChild(svgEl("line", { x1: padLeft, y1: padTop + plotH, x2: W - padRight, y2: padTop + plotH, class: "axis-line" }));
  labels.forEach((label, idx) => {
    const val = counts[idx];
    const barH = (val / maxVal) * (plotH - 10);
    const x = padLeft + idx * (barW + barGap);
    const y = padTop + plotH - barH;
    svg.appendChild(svgEl("rect", { x, y, width: barW, height: barH, fill: "#3c6e91", rx: 3 }));
    if (val > 0) {
      svg.appendChild(svgEl("text", { x: x + barW / 2, y: y - 6, "text-anchor": "middle", class: "value-label" })).textContent = val;
    }
    svg.appendChild(svgEl("text", { x: x + barW / 2, y: padTop + plotH + 16, "text-anchor": "middle", class: "bar-label" })).textContent = label;
  });
  box.innerHTML = "";
  box.appendChild(svg);
}

// Dual-axis line chart: month-on-month movement
function renderTrendChart() {
  const box = document.getElementById("trendChart");
  const trend = DATA.trend;
  const W = 560, H = 240, padLeft = 34, padRight = 34, padTop = 16, padBottom = 28;
  const plotW = W - padLeft - padRight, plotH = H - padTop - padBottom;
  const n = trend.length;
  const xStep = n > 1 ? plotW / (n - 1) : 0;

  const openVals = trend.map(t => t.open_risks);
  const avgVals = trend.map(t => t.avg_residual);
  const maxOpen = Math.max(1, ...openVals) * 1.15;
  const maxAvg = Math.max(1, ...avgVals) * 1.15;

  const xAt = i => padLeft + i * xStep;
  const yAtOpen = v => padTop + plotH - (v / maxOpen) * plotH;
  const yAtAvg = v => padTop + plotH - (v / maxAvg) * plotH;

  const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}` });
  svg.appendChild(svgEl("line", { x1: padLeft, y1: padTop + plotH, x2: W - padRight, y2: padTop + plotH, class: "axis-line" }));

  function linePath(vals, yFn) {
    return vals.map((v, i) => `${i === 0 ? "M" : "L"}${xAt(i).toFixed(1)},${yFn(v).toFixed(1)}`).join(" ");
  }

  svg.appendChild(svgEl("path", { d: linePath(openVals, yAtOpen), fill: "none", stroke: "#3c6e91", "stroke-width": 2 }));
  svg.appendChild(svgEl("path", { d: linePath(avgVals, yAtAvg), fill: "none", stroke: "#b5533c", "stroke-width": 2 }));

  trend.forEach((t, i) => {
    svg.appendChild(svgEl("circle", { cx: xAt(i), cy: yAtOpen(openVals[i]), r: 3, fill: "#3c6e91" }));
    svg.appendChild(svgEl("circle", { cx: xAt(i), cy: yAtAvg(avgVals[i]), r: 3, fill: "#b5533c" }));
    svg.appendChild(svgEl("text", { x: xAt(i), y: padTop + plotH + 16, "text-anchor": "middle", class: "bar-label" })).textContent = t.report_month.slice(5);
  });
  box.innerHTML = "";
  box.appendChild(svg);
}

function scorePill(score) {
  return `<span class="score-pill" style="background:${scorePillColor(score)}">${score}</span>`;
}

function renderTopRisks() {
  const tbody = document.querySelector("#topRisksTable tbody");
  tbody.innerHTML = DATA.top_risks.map(r => `
    <tr>
      <td>${r.risk_id}</td>
      <td>${r.title}</td>
      <td>${r.category}</td>
      <td>${r.owner}</td>
      <td>${scorePill(r.residual_score)}</td>
    </tr>`).join("");
}

function renderEmerging() {
  const tbody = document.querySelector("#emergingTable tbody");
  if (DATA.emerging_risks.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5">No risks increased in score since the previous reporting month.</td></tr>`;
    return;
  }
  tbody.innerHTML = DATA.emerging_risks.map(r => `
    <tr>
      <td>${r.risk_id}</td>
      <td>${r.title}</td>
      <td>${r.prev_residual_score}</td>
      <td>${scorePill(r.residual_score)}</td>
      <td>+${r.movement}</td>
    </tr>`).join("");
}

function renderOverdue() {
  const tbody = document.querySelector("#overdueTable tbody");
  if (DATA.overdue_actions.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5">No overdue actions at this reporting cut-off.</td></tr>`;
    return;
  }
  tbody.innerHTML = DATA.overdue_actions.map(a => `
    <tr>
      <td>${a.title} (${a.risk_id})</td>
      <td>${a.category}</td>
      <td>${a.action}</td>
      <td>${a.owner}</td>
      <td>${a.due_date}</td>
    </tr>`).join("");
}

renderKPIs();
populateCategoryFilter();
renderHeatmap("residual");
renderCategoryChart();
renderAgeingChart();
renderTrendChart();
renderTopRisks();
renderEmerging();
renderOverdue();

document.getElementById("btnResidual").addEventListener("click", () => renderHeatmap("residual"));
document.getElementById("btnInherent").addEventListener("click", () => renderHeatmap("inherent"));
</script>
</body>
</html>
"""


def main():
    html = HTML_TEMPLATE.replace("__DATA_JSON__", DATA_JSON)
    html = html.replace("__LATEST_MONTH__", DATA["kpis"]["latest_month"])
    html = html.replace("__OPEN_RISKS__", str(DATA["kpis"]["open_risks"]))
    html = html.replace("__OVERDUE_COUNT__", str(DATA["kpis"]["overdue_actions"]))
    with open("dashboard.html", "w") as f:
        f.write(html)
    print("Wrote dashboard.html")


if __name__ == "__main__":
    main()
