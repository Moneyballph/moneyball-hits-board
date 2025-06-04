
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Moneyball Phil", layout="centered")

# Load smaller logo
st.image("logo.png", width=120)

st.title("💥 Moneyball Phil: Daily Hit Probability Simulator")

if "hit_board" not in st.session_state:
    st.session_state.hit_board = []

player_name = st.text_input("Player Name")
avg_7 = st.number_input("Last 7 Days AVG", format="%.3f")
avg_pitcher = st.number_input("AVG vs Pitcher", format="%.3f")
avg_homeaway = st.number_input("Home/Away AVG", format="%.3f")
avg_handed = st.number_input("AVG vs Handedness", format="%.3f")
avg_season = st.number_input("Season AVG", format="%.3f")
odds = st.text_input("Sportsbook Odds (e.g. -150)")

weighted_avg = round(avg_7*0.2 + avg_pitcher*0.1 + avg_homeaway*0.2 + avg_handed*0.2 + avg_season*0.3, 3)
st.metric("Weighted AVG", weighted_avg)

def get_implied_prob(o):
    try:
        o = int(o)
        return round(100 / (o + 100), 4) if o > 0 else round(abs(o) / (abs(o) + 100), 4)
    except:
        return 0.0

def get_true_prob(avg):
    return round(1 - (1 - avg)**4, 4)

if st.button("Analyze Player"):
    true_prob = get_true_prob(weighted_avg)
    implied_prob = get_implied_prob(odds)
    ev = round((true_prob - implied_prob) * 100, 2)

    if true_prob >= 0.8:
        zone = "🔥 Elite"
    elif true_prob >= 0.7:
        zone = "🟢 Strong"
    elif true_prob >= 0.6:
        zone = "🟡 Moderate"
    else:
        zone = "🔴 Bad"

    st.session_state.hit_board.append({
        "Player": player_name,
        "Weighted AVG": weighted_avg,
        "True %": f"{true_prob*100:.1f}%",
        "Implied %": f"{implied_prob*100:.1f}%",
        "EV %": f"{ev}%",
        "Zone": zone
    })

if st.session_state.hit_board:
    df = pd.DataFrame(st.session_state.hit_board)
    st.subheader("📊 Live Hit Board")
    st.dataframe(df, use_container_width=True)
