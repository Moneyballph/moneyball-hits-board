
import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="Moneyball Phil: Daily Hit Probability Simulator", layout="centered")

# Display logo with smaller width
st.image("mbp_logo.png", use_column_width=False, width=250)

st.title("💥 Moneyball Phil: Daily Hit Probability Simulator")

st.markdown("Enter player stats below to simulate hit probability and evaluate betting value.")

# Input section
player_name = st.text_input("Player Name")
avg_last_7 = st.number_input("Last 7 Days AVG", step=0.001, format="%.3f")
avg_vs_pitcher = st.number_input("AVG vs Pitcher", step=0.001, format="%.3f")
avg_home_away = st.number_input("Home/Away AVG", step=0.001, format="%.3f")
avg_vs_handedness = st.number_input("AVG vs Handedness", step=0.001, format="%.3f")
season_avg = st.number_input("Season AVG", step=0.001, format="%.3f")
sportsbook_odds = st.number_input("Sportsbook Odds (e.g. -190 or +130)", step=1)

# Auto-calculate weighted average
weights = [0.2, 0.1, 0.2, 0.2, 0.3]
weighted_avg = round(
    avg_last_7 * weights[0]
    + avg_vs_pitcher * weights[1]
    + avg_home_away * weights[2]
    + avg_vs_handedness * weights[3]
    + season_avg * weights[4],
    3
)
st.markdown(f"**Weighted AVG:** `{weighted_avg}`")

# Simulate probability using binomial model (4 ABs assumed)
true_hit_prob = 1 - (1 - weighted_avg) ** 4
true_hit_pct = round(true_hit_prob * 100, 1)

# Sportsbook implied probability
if sportsbook_odds < 0:
    implied_prob = abs(sportsbook_odds) / (abs(sportsbook_odds) + 100)
else:
    implied_prob = 100 / (sportsbook_odds + 100)
implied_pct = round(implied_prob * 100, 1)

# Expected Value
ev = round((true_hit_prob - implied_prob) * 100, 1)

# Determine hit zone
if true_hit_pct >= 80:
    hit_zone = "🔥 Elite"
elif true_hit_pct >= 70:
    hit_zone = "🟢 Strong"
elif true_hit_pct >= 60:
    hit_zone = "🟡 Moderate"
else:
    hit_zone = "🔴 Bad"

# Analyze button
if st.button("Analyze Player"):
    st.subheader("📊 Simulation Results")
    st.markdown(f"**True Hit Probability:** `{true_hit_pct}%`")
    st.markdown(f"**Implied Probability:** `{implied_pct}%`")
    st.markdown(f"**Expected Value (EV%):** `{ev}%`")
    st.markdown(f"**Hit Zone:** {hit_zone}")

    # Save to hit board
    if "hit_board" not in st.session_state:
        st.session_state.hit_board = []
    st.session_state.hit_board.append({
        "Player": player_name,
        "True Hit %": true_hit_pct,
        "Implied %": implied_pct,
        "EV %": ev,
        "Zone": hit_zone
    })

# Live Hit Board
if "hit_board" in st.session_state and st.session_state.hit_board:
    st.markdown("---")
    st.subheader("🧢 Live Hit Board")
    df_board = pd.DataFrame(st.session_state.hit_board)
    st.dataframe(df_board, use_container_width=True)
