
import streamlit as st
import pandas as pd
from math import comb

st.set_page_config(page_title="Moneyball Phil: Daily Hit Probability Simulator", layout="wide")

st.title("💥 Moneyball Phil: Daily Hit Probability Simulator")
st.caption("Enter player stats below to calculate their true hit probability and EV value")

# Input form
with st.form("player_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Player Name")
        last7 = st.number_input("Last 7 Days AVG", min_value=0.0, max_value=1.0, step=0.001)
        vs_pitcher = st.number_input("AVG vs Pitcher", min_value=0.0, max_value=1.0, step=0.001)
    with col2:
        home_away = st.number_input("Home/Away AVG", min_value=0.0, max_value=1.0, step=0.001)
        handedness = st.number_input("AVG vs Handedness", min_value=0.0, max_value=1.0, step=0.001)
        season = st.number_input("Season AVG", min_value=0.0, max_value=1.0, step=0.001)
    with col3:
        odds = st.number_input("Sportsbook Odds (American)", step=1)
        at_bats = 4  # fixed

    submitted = st.form_submit_button("Analyze Player")

# Initialize session state
if "hit_board" not in st.session_state:
    st.session_state.hit_board = []

# Calculation functions
def calculate_weighted_avg(last7, vs_pitcher, home_away, handedness, season):
    return round((last7 * 0.2 + vs_pitcher * 0.1 + home_away * 0.2 + handedness * 0.2 + season * 0.3), 3)

def calculate_hit_probability(avg, ab=4):
    prob_hit = 1 - (1 - avg) ** ab
    return round(prob_hit * 100, 1)

def implied_probability(odds):
    return round((100 / (odds + 100)) * 100 if odds > 0 else (abs(odds) / (abs(odds) + 100)) * 100, 1)

def calculate_ev(true_prob, implied_prob):
    return round(true_prob - implied_prob, 1)

def hit_zone(prob):
    if prob >= 80:
        return "🔥 Elite"
    elif prob >= 70:
        return "🟢 Strong"
    elif prob >= 60:
        return "🟡 Moderate"
    else:
        return "🔴 Risky"

# Run when form submitted
if submitted and name:
    w_avg = calculate_weighted_avg(last7, vs_pitcher, home_away, handedness, season)
    true_prob = calculate_hit_probability(w_avg)
    implied_prob = implied_probability(odds)
    ev = calculate_ev(true_prob, implied_prob)
    zone = hit_zone(true_prob)

    st.session_state.hit_board.append({
        "Player": name,
        "Weighted AVG": w_avg,
        "True Hit %": true_prob,
        "Implied %": implied_prob,
        "EV%": ev,
        "Zone": zone,
    })

# Show Hit Board
if st.session_state.hit_board:
    st.subheader("📈 Live Hit Board")
    df = pd.DataFrame(st.session_state.hit_board)
    st.dataframe(df, use_container_width=True)
