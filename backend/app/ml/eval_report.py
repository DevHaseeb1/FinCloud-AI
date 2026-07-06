"""
Comprehensive ML Evaluation Report Generator with Plotly Charts.
Generates an interactive HTML report with charts, graphs, and metrics
for all three FinCloud-AI models: Anomaly Detection, Forecasting, and Cost Optimization.
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

from app.ml.prophet_model import ProphetForecastingModel
from app.ml.random_forest import RandomForestOptimizer
from app.services.anomaly_detection import AnomalyDetectionService
from app.services.optimization import OptimizationService
from app.services.preprocessing import DataPreprocessor

pio.templates.default = "plotly_dark"
logger = logging.getLogger(__name__)

ACCENT_COLORS = {
    "primary": "#00d4aa",
    "secondary": "#7c3aed",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
    "muted": "#6b7280",
}

SEVERITY_COLORS = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#3b82f6"}

PRIORITY_LABELS = {1: "Critical", 2: "High", 3: "Medium", 4: "Low"}

_PLOT_LAYOUT = dict(
    paper_bgcolor="#111318",
    plot_bgcolor="#111318",
    font=dict(color="#e5e7eb", size=11, family="Inter, sans-serif"),
    margin=dict(l=50, r=30, t=40, b=50),
    hovermode="x unified",
    xaxis=dict(showgrid=True, gridcolor="#1f2937", zerolinecolor="#374151"),
    yaxis=dict(showgrid=True, gridcolor="#1f2937", zerolinecolor="#374151"),
    legend=dict(bgcolor="rgba(17,19,24,0.8)", bordercolor="#1f2937"),
)


# ── Anomaly Detection Charts ────────────────────────────────────────────────

def anomaly_score_distribution(results_df: pd.DataFrame) -> go.Figure:
    scores = results_df["anomaly_score"].dropna()
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=scores, nbinsx=50, name="Score",
        marker_color=ACCENT_COLORS["primary"],
        opacity=0.75, histnorm="probability density",
    ))
    kde_x = np.linspace(scores.min(), scores.max(), 200)
    kde_y = _gaussian_kde(scores.values, kde_x)
    fig.add_trace(go.Scatter(
        x=kde_x, y=kde_y, name="Density",
        line=dict(color=ACCENT_COLORS["secondary"], width=2),
    ))
    fig.update_layout(
        title=dict(text="Anomaly Score Distribution", font=dict(size=14)),
        xaxis_title="Anomaly Score",
        yaxis_title="Density",
        **_PLOT_LAYOUT,
    )
    return fig


def anomaly_severity_pie(results_df: pd.DataFrame) -> go.Figure:
    sev = results_df["severity"].value_counts()
    colors = [SEVERITY_COLORS.get(s, "#6b7280") for s in sev.index]
    fig = go.Figure(data=[go.Pie(
        labels=sev.index.tolist(), values=sev.values.tolist(),
        marker=dict(colors=colors, line=dict(color="#111318", width=2)),
        textinfo="label+percent", hole=0.4,
    )])
    fig.update_layout(
        title=dict(text="Anomaly Severity Breakdown", font=dict(size=14)),
        **_PLOT_LAYOUT,
        showlegend=False,
    )
    return fig


def anomalies_over_time(results_df: pd.DataFrame) -> go.Figure:
    df = results_df.copy()
    if "timestamp" in df.columns:
        tcol = "timestamp"
    elif "date" in df.columns:
        tcol = "date"
    else:
        return go.Figure()
    df[tcol] = pd.to_datetime(df[tcol], errors="coerce")
    df = df.dropna(subset=[tcol]).sort_values(tcol)

    normal = df[df["anomaly_flag"] == 0]
    anomal = df[df["anomaly_flag"] == 1]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=normal[tcol], y=normal["cost"] if "cost" in normal else normal.get("total_cost", 0),
        mode="markers", name="Normal",
        marker=dict(color=ACCENT_COLORS["muted"], size=4, opacity=0.4),
    ))
    color_map = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#3b82f6"}
    for sev in ["High", "Medium", "Low"]:
        subset = anomal[anomal["severity"] == sev]
        if len(subset):
            fig.add_trace(go.Scatter(
                x=subset[tcol],
                y=subset["cost"] if "cost" in subset else subset.get("total_cost", 0),
                mode="markers", name=sev,
                marker=dict(color=color_map[sev], size=7, symbol="x",
                            line=dict(color="white", width=1)),
            ))
    fig.update_layout(
        title=dict(text="Anomalies Over Time", font=dict(size=14)),
        xaxis_title="Date", yaxis_title="Cost ($)",
        **_PLOT_LAYOUT,
    )
    return fig


def top_anomalous_services(results_df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    col = "service"
    if col not in results_df:
        return go.Figure()
    top = (
        results_df[results_df["anomaly_flag"] == 1]
        .groupby(col)
        .size()
        .sort_values(ascending=False)
        .head(top_n)
    )
    fig = go.Figure(data=[go.Bar(
        x=top.values[::-1], y=top.index[::-1],
        orientation="h", marker_color=ACCENT_COLORS["danger"],
        text=top.values[::-1], textposition="outside",
    )])
    fig.update_layout(
        title=dict(text=f"Top {top_n} Services by Anomaly Count", font=dict(size=14)),
        xaxis_title="Anomaly Count", yaxis_title="",
        **_PLOT_LAYOUT,
    )
    return fig


def daily_anomaly_rate(results_df: pd.DataFrame) -> go.Figure:
    df = results_df.copy()
    tcol = "timestamp" if "timestamp" in df else "date"
    if tcol not in df:
        return go.Figure()
    df[tcol] = pd.to_datetime(df[tcol], errors="coerce")
    df = df.dropna(subset=[tcol])
    daily = df.groupby(df[tcol].dt.date).agg(
        total=("anomaly_flag", "count"), anomalies=("anomaly_flag", "sum")
    )
    daily["rate"] = daily["anomalies"] / daily["total"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(daily.index), y=daily["rate"] * 100,
        mode="lines+markers", name="Anomaly Rate",
        line=dict(color=ACCENT_COLORS["warning"], width=2),
        marker=dict(size=4),
    ))
    fig.add_hline(
        y=daily["rate"].mean() * 100,
        line_dash="dash", line_color=ACCENT_COLORS["muted"],
        annotation_text=f"Avg: {daily['rate'].mean()*100:.1f}%",
    )
    fig.update_layout(
        title=dict(text="Daily Anomaly Rate", font=dict(size=14)),
        xaxis_title="Date", yaxis_title="Anomaly Rate (%)",
        **_PLOT_LAYOUT,
    )
    return fig


# ── Forecasting Charts ──────────────────────────────────────────────────────

def forecast_actual_vs_predicted(forecast_df: pd.DataFrame) -> go.Figure:
    req = {"ds", "yhat", "yhat_lower", "yhat_upper", "actual"}
    if not req.issubset(forecast_df.columns):
        return go.Figure()
    df = forecast_df.sort_values("ds")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["ds"], y=df["yhat_upper"], mode="lines",
        line=dict(width=0), showlegend=False, name="upper",
    ))
    fig.add_trace(go.Scatter(
        x=df["ds"], y=df["yhat_lower"], mode="lines",
        line=dict(width=0), fill="tonexty",
        fillcolor="rgba(0,212,170,0.15)", showlegend=False, name="lower",
    ))
    fig.add_trace(go.Scatter(
        x=df["ds"], y=df["yhat"], mode="lines+markers",
        name="Predicted", line=dict(color=ACCENT_COLORS["primary"], width=2),
        marker=dict(size=4),
    ))
    fig.add_trace(go.Scatter(
        x=df["ds"], y=df["actual"], mode="lines+markers",
        name="Actual", line=dict(color=ACCENT_COLORS["secondary"], width=2),
        marker=dict(size=4),
    ))
    fig.update_layout(
        title=dict(text="Forecast: Actual vs Predicted", font=dict(size=14)),
        xaxis_title="Date", yaxis_title="Cost ($)",
        **_PLOT_LAYOUT,
    )
    return fig


def forecast_residuals(forecast_df: pd.DataFrame) -> go.Figure:
    if "actual" not in forecast_df or "yhat" not in forecast_df:
        return go.Figure()
    residuals = forecast_df["actual"] - forecast_df["yhat"]
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=residuals.dropna(), nbinsx=40,
        marker_color=ACCENT_COLORS["info"],
        opacity=0.75, histnorm="probability density",
    ))
    mean_r = residuals.mean()
    std_r = residuals.std()
    fig.add_vline(
        x=mean_r, line_dash="dash", line_color=ACCENT_COLORS["danger"],
        annotation_text=f"Mean: {mean_r:.2f}",
    )
    fig.update_layout(
        title=dict(text="Prediction Residuals Distribution", font=dict(size=14)),
        xaxis_title="Residual (Actual - Predicted) ($)",
        yaxis_title="Density",
        **_PLOT_LAYOUT,
    )
    return fig


def forecast_residuals_vs_fitted(forecast_df: pd.DataFrame) -> go.Figure:
    if "actual" not in forecast_df or "yhat" not in forecast_df:
        return go.Figure()
    residuals = forecast_df["actual"] - forecast_df["yhat"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=forecast_df["yhat"], y=residuals,
        mode="markers", name="Residuals",
        marker=dict(color=ACCENT_COLORS["primary"], size=5, opacity=0.6),
    ))
    fig.add_hline(y=0, line_dash="dash", line_color=ACCENT_COLORS["muted"])
    fig.update_layout(
        title=dict(text="Residuals vs Fitted Values", font=dict(size=14)),
        xaxis_title="Predicted Cost ($)", yaxis_title="Residual ($)",
        **_PLOT_LAYOUT,
    )
    return fig


def forecast_horizon_error(forecast_df: pd.DataFrame) -> go.Figure:
    if "actual" not in forecast_df or "yhat" not in forecast_df or "ds" not in forecast_df:
        return go.Figure()
    df = forecast_df.sort_values("ds").copy()
    df["horizon"] = range(len(df))
    horizon_err = df.groupby("horizon").apply(
        lambda g: np.mean(np.abs((g["actual"].values - g["yhat"].values) /
                                  (g["actual"].values + 1e-6))) * 100
    ).reset_index()
    horizon_err.columns = ["horizon", "mape"]
    fig = go.Figure(data=[go.Bar(
        x=horizon_err["horizon"] + 1, y=horizon_err["mape"],
        marker_color=ACCENT_COLORS["info"],
        text=horizon_err["mape"].round(1), textposition="outside",
    )])
    fig.update_layout(
        title=dict(text="Forecast Error by Horizon (MAPE %)", font=dict(size=14)),
        xaxis_title="Days Ahead", yaxis_title="MAPE (%)",
        **_PLOT_LAYOUT,
    )
    return fig


def forecast_cumulative(forecast_df: pd.DataFrame) -> go.Figure:
    if "actual" not in forecast_df or "yhat" not in forecast_df:
        return go.Figure()
    df = forecast_df.sort_values("ds").copy()
    df["cum_actual"] = df["actual"].cumsum()
    df["cum_pred"] = df["yhat"].cumsum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["ds"], y=df["cum_actual"],
        mode="lines+markers", name="Actual (Cumulative)",
        line=dict(color=ACCENT_COLORS["secondary"], width=2),
        fill="tozeroy", fillcolor="rgba(124,58,237,0.1)",
    ))
    fig.add_trace(go.Scatter(
        x=df["ds"], y=df["cum_pred"],
        mode="lines+markers", name="Predicted (Cumulative)",
        line=dict(color=ACCENT_COLORS["primary"], width=2, dash="dot"),
    ))
    fig.update_layout(
        title=dict(text="Cumulative Cost: Actual vs Predicted", font=dict(size=14)),
        xaxis_title="Date", yaxis_title="Cumulative Cost ($)",
        **_PLOT_LAYOUT,
    )
    return fig


# ── Recommendation Charts ───────────────────────────────────────────────────

def rec_savings_by_type(recs: List[Dict]) -> go.Figure:
    if not recs:
        return go.Figure()
    by_type = {}
    for r in recs:
        t = r.get("recommendation_type", "unknown").replace("_", " ").title()
        by_type[t] = by_type.get(t, 0) + r.get("estimated_savings", 0)
    types = list(by_type.keys())
    savings = list(by_type.values())
    colors = [ACCENT_COLORS["primary"], ACCENT_COLORS["secondary"],
              ACCENT_COLORS["warning"], ACCENT_COLORS["info"]]
    fig = go.Figure(data=[go.Bar(
        x=types, y=savings,
        marker_color=colors[:len(types)],
        text=[f"${s:.0f}" for s in savings], textposition="outside",
    )])
    fig.update_layout(
        title=dict(text="Estimated Savings by Recommendation Type", font=dict(size=14)),
        xaxis_title="", yaxis_title="Estimated Savings ($)",
        **_PLOT_LAYOUT,
    )
    return fig


def rec_feature_importance(importances: Dict, top_n: int = 10) -> go.Figure:
    if not importances:
        return go.Figure()
    sorted_items = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:top_n]
    features = [x[0].replace("_", " ").title() for x in sorted_items][::-1]
    values = [x[1] for x in sorted_items][::-1]
    fig = go.Figure(data=[go.Bar(
        x=values, y=features, orientation="h",
        marker_color=ACCENT_COLORS["primary"],
        text=[f"{v:.4f}" for v in values], textposition="outside",
    )])
    fig.update_layout(
        title=dict(text=f"Top {top_n} Feature Importances", font=dict(size=14)),
        xaxis_title="Importance", yaxis_title="",
        **_PLOT_LAYOUT,
    )
    return fig


def rec_confidence_distribution(recs: List[Dict]) -> go.Figure:
    if not recs:
        return go.Figure()
    scores = [r.get("confidence_score", 0) for r in recs]
    fig = go.Figure(data=[go.Histogram(
        x=scores, nbinsx=15,
        marker_color=ACCENT_COLORS["secondary"],
        opacity=0.75,
    )])
    fig.update_layout(
        title=dict(text="Recommendation Confidence Distribution", font=dict(size=14)),
        xaxis_title="Confidence Score", yaxis_title="Count",
        **_PLOT_LAYOUT,
    )
    return fig


def rec_savings_by_service(recs: List[Dict], top_n: int = 10) -> go.Figure:
    if not recs:
        return go.Figure()
    by_svc = {}
    for r in recs:
        svc = r.get("service", "unknown").upper()
        by_svc[svc] = by_svc.get(svc, 0) + r.get("estimated_savings", 0)
    sorted_items = sorted(by_svc.items(), key=lambda x: x[1], reverse=True)[:top_n]
    services = [x[0] for x in sorted_items]
    savings = [x[1] for x in sorted_items]
    fig = go.Figure(data=[go.Bar(
        x=services, y=savings,
        marker_color=ACCENT_COLORS["warning"],
        text=[f"${s:.0f}" for s in savings], textposition="outside",
    )])
    fig.update_layout(
        title=dict(text=f"Top {top_n} Estimated Savings by Service", font=dict(size=14)),
        xaxis_title="", yaxis_title="Estimated Savings ($)",
        **_PLOT_LAYOUT,
    )
    return fig


def rec_priority_breakdown(recs: List[Dict]) -> go.Figure:
    if not recs:
        return go.Figure()
    df = pd.DataFrame(recs)
    if "recommendation_type" not in df or "priority" not in df:
        return go.Figure()
    df["type_label"] = df["recommendation_type"].str.replace("_", " ").str.title()
    df["priority_label"] = df["priority"].map(PRIORITY_LABELS)
    ct = df.pivot_table(index="type_label", columns="priority_label",
                        aggfunc="size", fill_value=0)
    priority_order = ["Critical", "High", "Medium", "Low"]
    ct = ct[[c for c in priority_order if c in ct.columns]]
    colors_priority = {"Critical": "#ef4444", "High": "#f59e0b",
                       "Medium": "#3b82f6", "Low": "#6b7280"}
    fig = go.Figure()
    for p in ct.columns:
        fig.add_trace(go.Bar(
            name=p, x=ct.index, y=ct[p],
            marker_color=colors_priority.get(p, "#6b7280"),
        ))
    fig.update_layout(
        barmode="stack",
        title=dict(text="Recommendations by Type and Priority", font=dict(size=14)),
        xaxis_title="", yaxis_title="Count",
        **_PLOT_LAYOUT,
    )
    return fig


# ── Summary Dashboard ───────────────────────────────────────────────────────

def _kpi_card(title: str, value: str, subtitle: str = "",
              color: str = ACCENT_COLORS["primary"]) -> str:
    return f"""
    <div style="background:#1a1b23;border-radius:8px;padding:16px;
                border-left:4px solid {color};display:flex;flex-direction:column;">
      <div style="font-size:12px;color:#9ca3af;text-transform:uppercase;letter-spacing:1px;">
        {title}
      </div>
      <div style="font-size:28px;font-weight:700;color:{color};margin:4px 0;">
        {value}
      </div>
      <div style="font-size:11px;color:#6b7280;">{subtitle}</div>
    </div>"""


def _render_kpis(anom_metrics: Dict, forecast_metrics: Dict,
                 rec_metrics: Dict, data_stats: Dict) -> str:
    anomaly_rate = anom_metrics.get("anomaly_rate", "N/A")
    if isinstance(anomaly_rate, float):
        anomaly_rate = f"{anomaly_rate * 100:.1f}%"

    mape = forecast_metrics.get("mape_pct", "N/A")
    if isinstance(mape, (int, float)):
        mape = f"{mape:.1f}%"

    rmse = forecast_metrics.get("rmse", "N/A")
    if isinstance(rmse, (int, float)):
        rmse = f"${rmse:.2f}"

    ci = forecast_metrics.get("within_95pct_ci", "N/A")
    if isinstance(ci, float):
        ci = f"{ci * 100:.1f}%"

    oob = rec_metrics.get("oob_score", "N/A")
    if isinstance(oob, float):
        oob = f"{oob:.4f}"

    savings = rec_metrics.get("total_estimated_savings", "N/A")
    if isinstance(savings, (int, float)):
        savings = f"${savings:,.0f}"

    n_recs = rec_metrics.get("n_recommendations", "N/A")

    return "".join([
        _kpi_card("Anomaly Rate", anomaly_rate, "Isolation Forest", ACCENT_COLORS["danger"]),
        _kpi_card("MAPE", mape, "Prophet Forecast", ACCENT_COLORS["warning"]),
        _kpi_card("RMSE", rmse, "Forecast Error", ACCENT_COLORS["info"]),
        _kpi_card("95% CI Coverage", ci, "Prophet Uncertainty", ACCENT_COLORS["primary"]),
        _kpi_card("OOB R²", oob, "RF+XGBoost Ensemble", ACCENT_COLORS["secondary"]),
        _kpi_card("Total Savings", savings, f"{n_recs} Recommendations", ACCENT_COLORS["info"]),
    ])


def _render_data_quality_table(df_raw: pd.DataFrame, df_proc: pd.DataFrame) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = [
        ("Report Generated", now),
        ("Raw Rows Loaded", f"{len(df_raw):,}"),
        ("Processed Rows", f"{len(df_proc):,}"),
        ("Date Range",
         f"{df_proc['date'].min().date()} to {df_proc['date'].max().date()}"
         if "date" in df_proc.columns else "N/A"),
        ("Unique Services", len(df_proc["service"].unique()) if "service" in df_proc else "N/A"),
        ("Unique Regions", len(df_proc["region"].unique()) if "region" in df_proc else "N/A"),
        ("Total Cost", f"${df_proc['total_cost'].sum():,.2f}" if "total_cost" in df_proc else "N/A"),
        ("Avg Daily Cost", f"${df_proc['total_cost'].mean():,.2f}" if "total_cost" in df_proc else "N/A"),
    ]
    trs = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in rows)
    return f"""
    <table style="width:100%;border-collapse:collapse;font-size:13px;">
      <tr style="background:#1f2937;"><th style="padding:8px;text-align:left;">Metric</th>
      <th style="padding:8px;text-align:left;">Value</th></tr>
      {trs}
    </table>"""


def _render_metrics_table(title: str, metrics: Dict) -> str:
    trs = "".join(
        f"<tr><td style='padding:6px 8px;border-bottom:1px solid #1f2937;'>{k}</td>"
        f"<td style='padding:6px 8px;border-bottom:1px solid #1f2937;font-weight:600;'>"
        f"{v}</td></tr>"
        for k, v in metrics.items()
    )
    return f"""
    <div style="margin-top:16px;">
      <h4 style="margin:0 0 8px 0;color:#00d4aa;">{title}</h4>
      <table style="width:100%;border-collapse:collapse;font-size:13px;
                    background:#1a1b23;border-radius:6px;overflow:hidden;">
        {trs}
      </table>
    </div>"""


def _clean_metric_key(k: str) -> str:
    return k.replace("_", " ").title().replace("Pct", "%").replace("P95", "P95")


# ── Build Report ────────────────────────────────────────────────────────────

def _figure_to_html(fig: go.Figure, chart_id: str) -> str:
    if not fig or not fig.data:
        return f"<div id='{chart_id}' style='color:#6b7280;padding:20px;text-align:center;'>No data available</div>"
    return pio.to_html(fig, include_plotlyjs=False, full_html=False,
                       div_id=chart_id, config={"displayModeBar": False,
                                                "responsive": True})


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FinCloud-AI Model Evaluation Report</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Inter',-apple-system,sans-serif; background:#0d0e12;
       color:#e5e7eb; padding:24px; }}
.container {{ max-width:1400px; margin:0 auto; }}
.header {{ text-align:center; padding:32px 0 24px; }}
.header h1 {{ font-size:28px; background:linear-gradient(135deg,#00d4aa,#7c3aed);
              -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.header p {{ color:#6b7280; font-size:14px; margin-top:4px; }}
.kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
             gap:12px; margin:24px 0; }}
.section {{ background:#111318; border:1px solid #1f2937; border-radius:12px;
            padding:24px; margin-bottom:24px; }}
.section h2 {{ font-size:18px; margin-bottom:16px; padding-bottom:8px;
               border-bottom:2px solid #1f2937; }}
.section h2 span {{ color:#00d4aa; }}
.chart-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(450px,1fr));
               gap:16px; }}
.chart-box {{ background:#15171e; border-radius:8px; padding:8px; }}
.chart-box h3 {{ font-size:13px; color:#9ca3af; padding:8px 8px 0; }}
.two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
@media(max-width:768px) {{ .two-col {{ grid-template-columns:1fr; }}
                          .chart-grid {{ grid-template-columns:1fr; }} }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ background:#1f2937; padding:8px; text-align:left; font-weight:600; }}
td {{ padding:8px; border-bottom:1px solid #1f2937; }}
tr:hover td {{ background:rgba(255,255,255,0.02); }}
</style>
</head>
<body>
<div class="container">
<div class="header">
  <h1>FinCloud-AI Model Evaluation Report</h1>
  <p>Comprehensive analysis of Anomaly Detection, Forecasting, and Cost Optimization models</p>
</div>

<div class="kpi-grid">{kpis}</div>

<div class="two-col">
  <div class="section">
    <h2><span>📊</span> Data Quality</h2>
    {data_quality}
  </div>
  <div class="section">
    <h2><span>📋</span> Forecast Metrics</h2>
    {forecast_metrics_table}
  </div>
</div>

<div class="section">
  <h2><span>🔍</span> 1. Anomaly Detection (Isolation Forest)</h2>
  <div class="two-col">
    {anom_metrics_table}
    <div></div>
  </div>
  <div class="chart-grid">
    <div class="chart-box">{anom_chart_1}</div>
    <div class="chart-box">{anom_chart_2}</div>
    <div class="chart-box">{anom_chart_3}</div>
    <div class="chart-box">{anom_chart_4}</div>
    <div class="chart-box" style="grid-column:1/-1;max-width:600px;margin:0 auto;">{anom_chart_5}</div>
  </div>
</div>

<div class="section">
  <h2><span>📈</span> 2. Forecasting (Prophet)</h2>
  <div class="chart-grid">
    <div class="chart-box" style="grid-column:1/-1;">{forecast_chart_1}</div>
    <div class="chart-box">{forecast_chart_2}</div>
    <div class="chart-box">{forecast_chart_3}</div>
    <div class="chart-box">{forecast_chart_4}</div>
    <div class="chart-box">{forecast_chart_5}</div>
  </div>
</div>

<div class="section">
  <h2><span>💰</span> 3. Cost Optimization (Random Forest + XGBoost)</h2>
  <div class="two-col">
    {rec_metrics_table}
    <div></div>
  </div>
  <div class="chart-grid">
    <div class="chart-box">{rec_chart_1}</div>
    <div class="chart-box">{rec_chart_2}</div>
    <div class="chart-box">{rec_chart_3}</div>
    <div class="chart-box">{rec_chart_4}</div>
    <div class="chart-box" style="grid-column:1/-1;max-width:600px;margin:0 auto;">{rec_chart_5}</div>
  </div>
</div>

<div style="text-align:center;padding:24px;color:#6b7280;font-size:12px;">
  Generated by FinCloud-AI Evaluation Report Generator &mdash; {timestamp}
</div>
</div>
</body>
</html>"""


def _gaussian_kde(values: np.ndarray, grid: np.ndarray, bw: Optional[float] = None) -> np.ndarray:
    n = len(values)
    if n < 2:
        return np.zeros_like(grid)
    if bw is None:
        bw = 1.06 * np.std(values) * n ** (-0.2)
    if bw < 1e-10:
        bw = 0.1
    out = np.zeros_like(grid)
    for v in values:
        out += np.exp(-0.5 * ((grid - v) / bw) ** 2)
    out /= (bw * np.sqrt(2 * np.pi) * n)
    return out


def build_report(
    anomaly_results_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    recommendations: List[Dict],
    feature_importances: Dict,
    anom_metrics: Dict,
    forecast_metrics: Dict,
    rec_metrics: Dict,
    df_raw: pd.DataFrame,
    df_processed: pd.DataFrame,
    output_path: str = "eval_report.html",
) -> str:
    logger.info("Building evaluation report...")

    anom_c1 = _figure_to_html(anomaly_score_distribution(anomaly_results_df), "anom-dist")
    anom_c2 = _figure_to_html(anomaly_severity_pie(anomaly_results_df), "anom-sev")
    anom_c3 = _figure_to_html(anomalies_over_time(anomaly_results_df), "anom-time")
    anom_c4 = _figure_to_html(top_anomalous_services(anomaly_results_df), "anom-top-svc")
    anom_c5 = _figure_to_html(daily_anomaly_rate(anomaly_results_df), "anom-daily")

    fcast_c1 = _figure_to_html(forecast_actual_vs_predicted(forecast_df), "fcast-act-vs-pred")
    fcast_c2 = _figure_to_html(forecast_residuals(forecast_df), "fcast-resid")
    fcast_c3 = _figure_to_html(forecast_residuals_vs_fitted(forecast_df), "fcast-resid-fit")
    fcast_c4 = _figure_to_html(forecast_horizon_error(forecast_df), "fcast-horizon")
    fcast_c5 = _figure_to_html(forecast_cumulative(forecast_df), "fcast-cum")

    rec_c1 = _figure_to_html(rec_savings_by_type(recommendations), "rec-savings-type")
    rec_c2 = _figure_to_html(rec_feature_importance(feature_importances), "rec-feat-imp")
    rec_c3 = _figure_to_html(rec_confidence_distribution(recommendations), "rec-conf")
    rec_c4 = _figure_to_html(rec_savings_by_service(recommendations), "rec-savings-svc")
    rec_c5 = _figure_to_html(rec_priority_breakdown(recommendations), "rec-priority")

    data_stats = {}
    kpis = _render_kpis(anom_metrics, forecast_metrics, rec_metrics, data_stats)
    data_quality = _render_data_quality_table(df_raw, df_processed)

    clean_anom = {_clean_metric_key(k): v for k, v in anom_metrics.items()}
    clean_fcast = {_clean_metric_key(k): v for k, v in forecast_metrics.items()}
    clean_rec = {_clean_metric_key(k): v for k, v in rec_metrics.items()}

    anom_mt = _render_metrics_table("Anomaly Detection Metrics", clean_anom)
    fcast_mt = _render_metrics_table("Forecast Metrics", clean_fcast)
    rec_mt = _render_metrics_table("Recommendation Metrics", clean_rec)

    html = _HTML_TEMPLATE.format(
        kpis=kpis,
        data_quality=data_quality,
        forecast_metrics_table=fcast_mt,
        anom_metrics_table=anom_mt,
        rec_metrics_table=rec_mt,
        anom_chart_1=anom_c1,
        anom_chart_2=anom_c2,
        anom_chart_3=anom_c3,
        anom_chart_4=anom_c4,
        anom_chart_5=anom_c5,
        forecast_chart_1=fcast_c1,
        forecast_chart_2=fcast_c2,
        forecast_chart_3=fcast_c3,
        forecast_chart_4=fcast_c4,
        forecast_chart_5=fcast_c5,
        rec_chart_1=rec_c1,
        rec_chart_2=rec_c2,
        rec_chart_3=rec_c3,
        rec_chart_4=rec_c4,
        rec_chart_5=rec_c5,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"Report saved to {output_path}")
    return output_path


def run_and_build_report(
    csv_path: str,
    output_path: str = "eval_report.html",
    contamination: float = 0.02,
    forecast_periods: int = 30,
    sample_size: int = 5000,
) -> str:
    logger.info(f"Loading data from {csv_path}")
    df_raw = pd.read_csv(csv_path, low_memory=False)
    logger.info(f"Loaded {len(df_raw):,} rows")

    df_map = df_raw.rename(columns={
        "lineItem/UnblendedCost": "cost",
        "lineItem/UsageStartDate": "timestamp",
        "lineItem/ProductCode": "service",
        "product/region": "region",
        "lineItem/UsageAmount": "usage_amount",
        "lineItem/UsageType": "usage_type",
        "lineItem/LineItemType": "line_item_type",
        "lineItem/ResourceId": "resource_id",
        "lineItem/Operation": "operation",
        "product/productFamily": "product_family",
        "pricing/term": "pricing_term",
        "product/instanceType": "instance_type",
    })
    if "timestamp" in df_map.columns:
        df_map["timestamp"] = pd.to_datetime(df_map["timestamp"], errors="coerce")
    df_map["cost"] = pd.to_numeric(df_map["cost"], errors="coerce").fillna(0)
    df_map["usage_amount"] = pd.to_numeric(df_map["usage_amount"], errors="coerce").fillna(0)
    df_map["usage_quantity"] = df_map["usage_amount"]
    for col in ["service", "region", "usage_type", "line_item_type",
                "resource_id", "operation", "product_family", "pricing_term",
                "instance_type"]:
        df_map[col] = df_map[col].fillna("unknown").astype(str).str.lower()
    df_map["account_id"] = "unknown"
    df_map["environment"] = "unknown"
    df_map = df_map.dropna(subset=["timestamp"])

    logger.info(f"After preprocessing: {len(df_map):,} rows")

    eval_df = df_map
    if len(df_map) > sample_size:
        eval_df = df_map.sample(n=sample_size, random_state=42)
        logger.info(f"Sampled to {sample_size} rows for anomaly detection")

    logger.info("Training Anomaly Detection...")
    anomaly_svc = AnomalyDetectionService(contamination=contamination)
    anomaly_svc.train(df_map)
    anomaly_results_df = anomaly_svc.detect_anomalies(eval_df)
    anom_metrics = {
        "anomaly_rate": round(int(anomaly_results_df["anomaly_flag"].sum()) /
                              max(len(anomaly_results_df), 1), 4),
        "samples evaluated": len(anomaly_results_df),
        "anomalies found": int(anomaly_results_df["anomaly_flag"].sum()),
        "score mean": round(anomaly_results_df["anomaly_score"].mean(), 4),
        "score std": round(anomaly_results_df["anomaly_score"].std(), 4),
        "severity distribution": anomaly_results_df["severity"].value_counts().to_dict(),
    }

    logger.info("Training Forecasting model...")
    df_proc = DataPreprocessor.full_preprocessing_pipeline(df_map)
    train_df = df_proc.groupby("date").agg({"total_cost": "sum"}).reset_index()
    train_df.columns = ["ds", "y"]
    split = int(len(train_df) * 0.8)
    if split < 14:
        raise ValueError("Insufficient data for forecast evaluation")
    train = train_df.iloc[:split].copy()
    train["ds"] = train["ds"].dt.tz_localize(None)
    test = train_df.iloc[split:].copy()
    test["ds"] = test["ds"].dt.tz_localize(None)

    forecast_model = ProphetForecastingModel()
    forecast_model.train(train, model_name="eval", tune=False)
    forecast_result = forecast_model.forecast(periods=len(test), model_name="eval")
    forecast_result = forecast_result.merge(
        test.rename(columns={"y": "actual"}), on="ds", how="left"
    ).dropna(subset=["actual"])

    actuals = forecast_result["actual"].values
    predicted = forecast_result["yhat"].values
    forecast_metrics = {
        "mape_pct": round(np.mean(np.abs((actuals - predicted) / (actuals + 1e-6))) * 100, 2),
        "rmse": round(np.sqrt(np.mean((actuals - predicted) ** 2)), 2),
        "mae": round(np.mean(np.abs(actuals - predicted)), 2),
        "within_95pct_ci": round(
            ((actuals >= forecast_result["yhat_lower"].values) &
             (actuals <= forecast_result["yhat_upper"].values)).mean(), 4
        ),
        "n_train": len(train),
        "n_test": len(forecast_result),
    }

    logger.info("Training Cost Optimization model...")
    opt_svc = OptimizationService()
    opt_svc.train(df_proc)
    recs = opt_svc.get_recommendations(df_proc, top_n=20)
    importances = opt_svc.get_feature_importance()
    rec_metrics = {
        "n_recommendations": len(recs),
        "total_estimated_savings": round(sum(r["estimated_savings"] for r in recs), 2),
        "oob_score": round(opt_svc.model.metrics.oob_score, 4) if opt_svc.model.metrics and opt_svc.model.metrics.oob_score else None,
    }
    by_type = {}
    for r in recs:
        t = r["recommendation_type"]
        by_type[t] = by_type.get(t, 0) + 1
    rec_metrics["by_type"] = by_type

    return build_report(
        anomaly_results_df=anomaly_results_df,
        forecast_df=forecast_result,
        recommendations=recs,
        feature_importances=importances,
        anom_metrics=anom_metrics,
        forecast_metrics=forecast_metrics,
        rec_metrics=rec_metrics,
        df_raw=df_raw,
        df_processed=df_proc,
        output_path=output_path,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    import sys
    csv = sys.argv[1] if len(sys.argv) > 1 else \
        r"C:\Users\Haseeb\Desktop\FinCloud-AI\Fincloud-cur-enhanced-v2.csv"
    out = sys.argv[2] if len(sys.argv) > 2 else "eval_report.html"
    run_and_build_report(csv, out)
    print(f"\nReport generated: {os.path.abspath(out)}")
