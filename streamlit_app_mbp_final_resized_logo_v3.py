
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Moneyball Phil", layout="centered")

# Smaller logo with correct container width setting
st.image("mbp_logo.png", use_container_width=True, caption="Moneyball Phil: Daily Hit Probability Simulator")

st.title("Moneyball Phil: Daily Hit Probability Simulator")

# Initialize session state
if "hit_board" not in st.session_state:
    st.session_state.hit_board = []

# User inputs
player_name = st.text_input("Player Name")
col1, col2, col3 = st.columns(3)
with col1:
    last7 = st.number_input("Last 7 Days AVG", format="%.3f")
    vs_pitcher = st.number_input("AVG vs Pitcher", format="%.3f")
with col2:
    home_away = st.number_input("Home/Away AVG", format="%.3f")
    vs_handed = st.number_input("AVG vs Handedness", format="%.3f")
with col3:
    season_avg = st.number_input("Season AVG", format="%.3f")
    odds = st.text_input("Sportsbook Odds (e.g., -175)")

# Weighted average calculation
weighted_avg = round(
    (last7 * 0.25 + vs_pitcher * 0.1 + home_away * 0.15 + vs_handed * 0.2 + season_avg * 0.3), 3
)

st.metric("Weighted AVG", weighted_avg)

# Calculate true hit probability (binomial method over 4 ABs)
def hit_probability(avg, ab=4):
    miss_prob = (1 - avg)
    return round(1 - (miss_prob ** ab), 3)

# Calculate implied probability from odds
def implied_prob(odds_str):
    try:
        o = int(odds_str)
        if o > 0:
            return round(100 / (o + 100), 4)
        else:
            return round(abs(o) / (abs(o) + 100), 4)
    except:
        return None

if st.button("Analyze Player"):
    true_prob = hit_probability(weighted_avg)
    implied = implied_prob(odds)
    ev = round((true_prob - implied) * 100, 2) if implied else None

    # Hit zone categorization
    if true_prob >= 0.80:
        zone = "🔥 Elite"
    elif true_prob >= 0.70:
        zone = "🟢 Strong"
    elif true_prob >= 0.60:
        zone = "🟡 Moderate"
    else:
        zone = "🔴 Bad"

    st.success(f"True Hit Probability: {true_prob*100:.1f}%")
    st.info(f"Implied Probability: {implied*100:.1f}%" if implied else "Implied probability: Invalid odds")
    st.write(f"Expected Value: {ev:.2f}%" if ev is not None else "Invalid EV")
    st.write(f"Hit Zone: {zone}")

    st.session_state.hit_board.append({
        "Player": player_name,
        "Weighted AVG": weighted_avg,
        "True %": f"{true_prob*100:.1f}%",
        "Implied %": f"{implied*100:.1f}%" if implied else "Invalid",
        "EV %": f"{ev:.2f}%" if ev else "Invalid",
        "Hit Zone": zone
    })

# Display live hit board
if st.session_state.hit_board:
    st.subheader("Live Hit Board")
    st.dataframe(pd.DataFrame(st.session_state.hit_board))
