
import streamlit as st
import pandas as pd
from scipy.stats import binom

# Set up the dashboard
st.set_page_config(page_title="Moneyball Phil: Hit Simulator", layout="wide")

# Display logo from local file in the same repo
st.image("moneyball_logo.png", width=300)

st.title("⚾ Moneyball Phil: Daily Hit Probability Simulator")

if "results_table" not in st.session_state:
    st.session_state["results_table"] = []

st.header("🔍 Enter Player Stats")

player_name = st.text_input("Player Name")
last7_avg = st.number_input("Last 7 Days AVG", min_value=0.0, max_value=1.0, format="%.4f")
vs_pitcher_avg = st.number_input("AVG vs Pitcher (enter 0 if none)", min_value=0.0, max_value=1.0, format="%.4f")
home_away_avg = st.number_input("Home/Away AVG", min_value=0.0, max_value=1.0, format="%.4f")
handedness_avg = st.number_input("AVG vs Handedness", min_value=0.0, max_value=1.0, format="%.4f")
season_avg = st.number_input("Season AVG", min_value=0.0, max_value=1.0, format="%.4f")

# Calculate weighted AVG
weight_avg = (
    last7_avg * 0.3 +
    vs_pitcher_avg * 0.3 +
    home_away_avg * 0.1 +
    handedness_avg * 0.2 +
    season_avg * 0.1
)
st.markdown(f"### 📐 Weighted AVG: `{weight_avg:.4f}`")

odds = st.text_input("Sportsbook Odds (e.g. -250 or +120)")

def classify_hit_zone(p):
    if p >= 80:
        return "🔥 Elite"
    elif p >= 70:
        return "✅ Strong"
    elif p >= 60:
        return "⚠️ Moderate"
    else:
        return "❌ Low"

if st.button("Analyze Player"):
    true_prob = 1 - binom.pmf(0, 4, weight_avg)

    try:
        odds_val = int(odds)
        implied_prob = abs(odds_val) / (abs(odds_val) + 100) if odds_val < 0 else 100 / (odds_val + 100)
    except:
        implied_prob = 0.0

    ev = (true_prob - implied_prob) * 100
    hit_zone = classify_hit_zone(true_prob * 100)
    value_tag = "🔥 High Value" if ev >= 15 else "—"

    result = {
        "Player": player_name,
        "True Hit %": f"{true_prob*100:.1f}%",
        "Implied %": f"{implied_prob*100:.1f}%",
        "EV %": f"{ev:.1f}%",
        "Hit Zone": hit_zone,
        "Value": value_tag
    }
    st.session_state["results_table"].append(result)

if st.session_state["results_table"]:
    st.markdown("### 📊 Live Hit Board")
    st.dataframe(pd.DataFrame(st.session_state["results_table"]))
