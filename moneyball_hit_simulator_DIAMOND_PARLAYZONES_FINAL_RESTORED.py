
import streamlit as st
import base64
import pandas as pd

# Set up background
def set_background(img_file):
    with open(img_file, "rb") as f:
        img_bytes = f.read()
    encoded = base64.b64encode(img_bytes).decode()
    css = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    '''
    st.markdown(css, unsafe_allow_html=True)

set_background("baseball_diamond_bg.png")
st.image("moneyball_logo.png", width=180)
st.title("💰 Moneyball Phil: Daily Hit Probability Simulator")

with st.form("player_form"):
    name = st.text_input("Player Name")
    season_avg = st.number_input("Season AVG", 0.0, 1.0, step=0.0001, format="%.4f")
    last7 = st.number_input("Last 7 Days AVG", 0.0, 1.0, step=0.0001, format="%.4f")
    split_avg = st.number_input("Split AVG (Home/Away or AL/NL)", 0.0, 1.0, step=0.0001, format="%.4f")
    hand_avg = st.number_input("AVG vs Pitcher Handedness", 0.0, 1.0, step=0.0001, format="%.4f")
    pitcher_avg = st.number_input("AVG vs Pitcher", 0.0, 1.0, step=0.0001, format="%.4f")
    odds = st.number_input("Sportsbook Odds (American)", step=1)
    submitted = st.form_submit_button("Calculate Player")

if "hit_board" not in st.session_state:
    st.session_state.hit_board = []

if submitted:
    weighted_avg = round(0.3 * last7 + 0.2 * split_avg + 0.2 * hand_avg + 0.1 * pitcher_avg + 0.2 * season_avg, 4)
    true_prob = 1 - (1 - weighted_avg) ** 4
    if odds < 0:
        implied_prob = abs(odds) / (abs(odds) + 100)
    else:
        implied_prob = 100 / (odds + 100)
    ev = (true_prob - implied_prob) * 100
    zone = "Elite" if true_prob >= 0.80 else "Strong" if true_prob >= 0.70 else "Moderate" if true_prob >= 0.60 else "Bad"
    st.session_state.hit_board.append({
        "Player": name,
        "True Probability": round(true_prob * 100, 1),
        "Implied Probability": round(implied_prob * 100, 1),
        "EV%": round(ev, 1),
        "Zone": zone
    })

# Show Top Hit Board
if st.session_state.hit_board:
    board_df = pd.DataFrame(st.session_state.hit_board)
    board_df.insert(0, "Rank", range(1, len(board_df) + 1))
    st.subheader("📋 Top Hit Board")
    st.dataframe(board_df)

# Parlay Builder
st.subheader("🧮 Build a 2 or 3-Leg Parlay")
with st.form("parlay_form"):
    num_legs = st.radio("Number of Legs", [2, 3], horizontal=True)
    legs = []
    for i in range(num_legs):
        legs.append(st.number_input(f"True Hit Probability for Player {i + 1} (%)", 0.0, 100.0, step=0.1) / 100)
    parlay_odds = st.number_input("Sportsbook Parlay Odds (American)", step=1)
    build = st.form_submit_button("Calculate Parlay Value")

if build:
    from functools import reduce
    parlay_prob = reduce(lambda x, y: x * y, legs)
    if parlay_odds < 0:
        implied_parlay_prob = abs(parlay_odds) / (abs(parlay_odds) + 100)
    else:
        implied_parlay_prob = 100 / (parlay_odds + 100)
    ev_parlay = (parlay_prob - implied_parlay_prob) * 100
    zone = "Elite" if parlay_prob >= 0.80 else "Strong" if parlay_prob >= 0.70 else "Moderate" if parlay_prob >= 0.60 else "Bad"

    st.markdown(f"**Parlay True Probability:** {parlay_prob:.2%}")
    st.markdown(f"**Parlay Implied Probability:** {implied_parlay_prob:.2%}")
    st.markdown(f"**Parlay EV%:** {ev_parlay:.2f}%")
    st.markdown(f"**Parlay Zone:** 🟢 {zone}")
