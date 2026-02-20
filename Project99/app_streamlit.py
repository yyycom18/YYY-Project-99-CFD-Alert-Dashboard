"""
Project99 — Phase 2 Transparent Visualization Layer
Streamlit dashboard: Scanner View + Deep Structure View.
Real 15m data via yfinance (local only).
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from Project99 import score, get_resampled, CONDITION_NAMES
from Project99.visualization import build_three_panel_figure
from Project99.visualization.market_data import fetch_15m_data


st.set_page_config(page_title="Project99 Scanner", layout="wide")

SYMBOL_MAP = {
    "XAUUSD": "GC=F",
    "EURUSD": "EURUSD=X",
    "AUDUSD": "AUDUSD=X",
    "HK50": "^HSI",
}


def run_scanner(assets_data):
    """Layer 1 — Scanner View: table, click asset → Deep Structure."""
    st.title("Project99 — Scanner View")
    rows = []
    for asset, df in assets_data.items():
        res = score(df, freq_minutes=15)
        rows.append({
            "Asset": asset,
            "long_score": res["long_score"],
            "short_score": res["short_score"],
            "bias": res["bias"],
            "alert_long": res["alert_long"],
            "alert_short": res["alert_short"],
        })
    table_df = pd.DataFrame(rows)
    st.dataframe(table_df, use_container_width=True, hide_index=True)
    selected = st.selectbox("Open Deep Structure View", options=list(assets_data.keys()), key="scanner_select")
    return selected


def score_panel(result):
    """Score panel at top: Long X/7, Short Y/7, Bias with colors."""
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Long Score** : <span style='color:green'>{result['long_score']} / 7</span>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"**Short Score** : <span style='color:red'>{result['short_score']} / 7</span>", unsafe_allow_html=True)
    with c3:
        bias = result["bias"]
        if bias > 0:
            color = "green"
        elif bias < 0:
            color = "red"
        else:
            color = "gray"
        st.markdown(f"**Bias** : <span style='color:{color}'>{bias}</span>", unsafe_allow_html=True)


def condition_breakdown(result):
    """Collapsible: two columns Long / Short with status + short explanation."""
    with st.expander("Condition Details"):
        left, right = st.columns(2)
        with left:
            st.subheader("Long conditions")
            for name in CONDITION_NAMES:
                v = result["long_conditions"].get(name, False)
                st.markdown(f"- **{name}**: {'✅ True' if v else '❌ False'}")
        with right:
            st.subheader("Short conditions")
            for name in CONDITION_NAMES:
                v = result["short_conditions"].get(name, False)
                st.markdown(f"- **{name}**: {'✅ True' if v else '❌ False'}")


def deep_structure_view(asset: str, df_15m: pd.DataFrame, result: dict):
    """Layer 2 — Score panel + 3 charts + condition breakdown + sidebar toggles."""
    st.title(f"Deep Structure — {asset}")
    score_panel(result)
    condition_breakdown(result)

    with st.sidebar:
        st.header("Condition toggles")
        show_trend = st.checkbox("Trend", value=True, key="t_trend")
        show_impulse = st.checkbox("Impulse Break", value=True, key="t_impulse")
        show_stop_hunt = st.checkbox("Stop Hunt", value=True, key="t_stophunt")
        show_stop_money = st.checkbox("Stop Money", value=True, key="t_stopmoney")
        show_zone = st.checkbox("Zone", value=True, key="t_zone")
        show_fib = st.checkbox("Fib", value=True, key="t_fib")
        show_session = st.checkbox("Session", value=True, key="t_session")
        show_blocking = st.checkbox("Blocking", value=True, key="t_blocking")

    df_1h, df_4h = get_resampled(df_15m, 15)
    fig = build_three_panel_figure(
        df_15m, df_1h, df_4h, result,
        show_trend=show_trend,
        show_impulse=show_impulse,
        show_stop_hunt=show_stop_hunt,
        show_stop_money=show_stop_money,
        show_zone=show_zone,
        show_fib=show_fib,
        show_session=show_session,
        show_blocking=show_blocking,
        score_fn=score,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Patch 7 — Chart Legend (圖表圖形 / 顏色說明)
    with st.expander("Chart Legend – 圖表圖形 / 顏色說明"):
        legend_data = {
            "Element": [
                "Demand Zone",
                "Supply Zone",
                "Stop Hunt Zone",
                "Stop Money",
                "Blocking Level",
                "Swing High",
                "Swing Low",
                "Weekly High Score",
            ],
            "Color / Shape": [
                "Orange (transparent)",
                "Grey (transparent)",
                "Light Green / Light Red Band",
                "Green / Red Dashed Line",
                "Black Thick Line",
                "Triangle Up",
                "Triangle Down",
                "Green / Red Star",
            ],
            "Meaning": [
                "上升禁區",
                "下降禁區",
                "0.5–0.7 回調區域",
                "前方流動性目標",
                "大支持 / 大阻力",
                "結構高點",
                "結構低點",
                "最近4週高分訊號",
            ],
        }
        st.table(pd.DataFrame(legend_data))

    # Patch 8 — Strategy Conditions (七大條件說明)
    with st.expander("Strategy Conditions – 七大條件說明"):
        conditions_data = {
            "Condition": [
                "Trend",
                "Impulse Break",
                "Stop Hunt",
                "Stop Money",
                "Zone",
                "Fibonacci",
                "Session",
            ],
            "Timeframe": [
                "4H",
                "1H",
                "1H",
                "1H",
                "Multi TF",
                "15M",
                "1H",
            ],
            "Description": [
                "判斷大方向（Higher High / Lower Low 結構）",
                "原生動能破結構",
                "回調 0.5–0.7 區域內流動性聚集",
                "前方雙頂 / 雙底流動性目標",
                "機構成本禁區",
                "部署回調區域",
                "EU / US 行為觸發確認",
            ],
        }
        st.table(pd.DataFrame(conditions_data))


def main():
    if "refresh_trigger" not in st.session_state:
        st.session_state.refresh_trigger = 0
    if "assets_data" not in st.session_state:
        st.session_state.assets_data = {}

    if st.button("Refresh Data"):
        st.session_state.refresh_trigger += 1
        st.session_state.assets_data = {}

    if not st.session_state.assets_data:
        for asset in SYMBOL_MAP:
            selected_symbol = SYMBOL_MAP[asset]
            df = fetch_15m_data(selected_symbol, lookback_days=10)
            if not df.empty:
                st.session_state.assets_data[asset] = df
        if not st.session_state.assets_data:
            st.error("Data fetch failed.")
            st.stop()

    assets_data = st.session_state.assets_data
    selected = run_scanner(assets_data)
    df_15m = assets_data[selected]
    result = score(df_15m, freq_minutes=15)
    st.divider()
    deep_structure_view(selected, df_15m, result)


if __name__ == "__main__":
    main()
